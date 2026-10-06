"""Evaluate a real trained checkpoint; never downloads missing model weights."""
import argparse
import json
from pathlib import Path
from common import ROOT, CLASS_NAMES, prepare_dataset, print_summary, save_resolved_dataset, validate_class_names


def main():
    parser = argparse.ArgumentParser(description='Evaluate CivicEye detection metrics on held-out labels.')
    parser.add_argument('--weights', default=str(ROOT / 'models' / 'civiceye.pt'))
    parser.add_argument('--data', default=str(Path(__file__).with_name('dataset.yaml')))
    parser.add_argument('--split', choices=['val', 'test'], default='val')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--project', default=str(ROOT / 'training' / 'validation'))
    parser.add_argument('--name', default='civiceye')
    args = parser.parse_args()
    weights = Path(args.weights).expanduser().resolve()
    if not weights.is_file():
        parser.exit(2, f'Trained checkpoint not found: {weights}\nTrain your sourced dataset first; no weights will be downloaded.\n')
    if args.imgsz < 32 or args.imgsz % 32 or args.batch <= 0:
        parser.error('Use a positive batch and image size divisible by 32.')
    try:
        config, summary = prepare_dataset(args.data, (args.split,), require_all_classes=False)
        print_summary(summary)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Validation dataset not ready: {exc}\n')
    from ultralytics import YOLO
    model = YOLO(str(weights))
    validate_class_names(model.names)
    if model.task != 'detect':
        parser.error('Use a detection checkpoint with the bounding-box dataset.')
    metrics = model.val(data=str(save_resolved_dataset(config)), split=args.split, imgsz=args.imgsz,
                        batch=args.batch, device=args.device, workers=0,
                        project=str(Path(args.project).resolve()), name=args.name,
                        exist_ok=False, plots=True, save_json=False)
    report = {'split': args.split, 'weights': str(weights), 'precision': float(metrics.box.mp),
              'recall': float(metrics.box.mr), 'mAP50': float(metrics.box.map50),
              'mAP50_95': float(metrics.box.map), 'per_class': {}, 'speed_ms': metrics.speed}
    # Report only metrics for classes actually represented in held-out labels.
    present = {int(class_id): index for index, class_id in enumerate(metrics.box.ap_class_index)}
    for class_id, name in CLASS_NAMES.items():
        values = metrics.box.class_result(present[class_id]) if class_id in present else (None,) * 4
        report['per_class'][name] = {'ground_truth_objects': summary[args.split]['objects'][name],
                                    **{key: float(value) if value is not None else None
                                       for key, value in zip(('precision', 'recall', 'mAP50', 'mAP50_95'), values)}}
    if getattr(metrics, 'confusion_matrix', None) is not None:
        report['confusion_matrix'] = metrics.confusion_matrix.matrix.tolist()
        report['confusion_matrix_labels'] = list(CLASS_NAMES.values()) + ['background']
        report['confusion_matrix_axes'] = 'rows predicted, columns actual; detector default validation confidence/IoU'
    output = Path(metrics.save_dir) / 'civiceye-metrics.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    print(f'VALIDATION REPORT: {output.resolve()}')
    print('Review confusion matrices and example predictions; inspect background false positives and real-road/demo performance separately.')


if __name__ == '__main__':
    main()
