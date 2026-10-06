"""Prepare/check sourced data, then train only when explicitly run by the team."""
import argparse
from pathlib import Path
import shutil
from datetime import datetime, timezone
from common import ROOT, prepare_dataset, save_resolved_dataset, print_summary, validate_class_names


def main():
    parser = argparse.ArgumentParser(description='Train CivicEye v1: pothole, garbage, waterlogging.')
    parser.add_argument('--data', default=str(Path(__file__).with_name('dataset.yaml')))
    parser.add_argument('--pretrained', default='yolo11n.pt', help='Official nano weights, or a trusted local pretrained .pt file')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--device', default='cpu', help='cpu for laptop; 0 for Colab CUDA')
    parser.add_argument('--workers', type=int, default=0, help='0 is reliable on Windows/Colab notebooks')
    parser.add_argument('--project', default=str(ROOT / 'training' / 'runs'))
    parser.add_argument('--name', default='civiceye')
    parser.add_argument('--check-only', action='store_true', help='Check dataset without downloading weights or training')
    parser.add_argument('--no-deploy', action='store_true', help='Preserve best.pt but do not copy it to models/civiceye.pt')
    args = parser.parse_args()
    if args.epochs <= 0 or args.batch <= 0 or args.imgsz < 32 or args.imgsz % 32 or args.workers < 0:
        parser.error('epochs/batch must be positive, imgsz a positive multiple of 32, workers nonnegative.')
    if not args.pretrained.endswith('.pt'):
        parser.error('Use pretrained .pt weights; YAML architecture-only training is not this transfer-learning pipeline.')
    try:
        config, summary = prepare_dataset(args.data)
        print_summary(summary)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Dataset not ready: {exc}\nNo training was started.\n')
    if args.check_only:
        print('Dataset checks passed. No weights downloaded; no training started.')
        return
    from ultralytics import YOLO
    prepared = save_resolved_dataset(config)
    model = YOLO(args.pretrained)
    if model.task != 'detect':
        parser.error('This pipeline uses object-detection bounding-box labels. Supply detection pretrained weights.')
    model.train(data=str(prepared), epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                device=args.device, workers=args.workers, project=str(Path(args.project).resolve()),
                name=args.name, exist_ok=False, pretrained=True, save=True, val=True, plots=True,
                seed=42, deterministic=True)
    best = Path(model.trainer.best).resolve()
    if not best.is_file():
        raise RuntimeError('Training ended without best.pt. Review the training logs; no deployment was performed.')
    best_model = YOLO(str(best))
    validate_class_names(best_model.names)
    print(f'BEST MODEL: {best}')
    print(f'TRAINING RESULTS: {best.parent.parent}')
    if not args.no_deploy:
        destination = ROOT / 'models' / 'civiceye.pt'
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix('.pt.tmp')
        shutil.copy2(best, temporary)
        if destination.exists():
            stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
            backup = destination.with_name(f'civiceye.previous-{stamp}.pt')
            shutil.copy2(destination, backup)
            print(f'PREVIOUS MODEL PRESERVED: {backup}')
        temporary.replace(destination)
        print(f'DEPLOYED MODEL: {destination}')
        print('Restart FastAPI and check /health for model_loaded=true. This does not certify model accuracy; validate it separately.')


if __name__ == '__main__':
    main()
