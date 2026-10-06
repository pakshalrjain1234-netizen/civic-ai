"""Local training entry point. Candidate weights stay out of the inference directory."""
import argparse,json,time,tempfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'training/matplotlib-cache'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--imgsz',type=int,choices=[640,768],default=640)
    parser.add_argument('--epochs',type=int,default=80);parser.add_argument('--allow-cpu',action='store_true')
    parser.add_argument('--resume',action='store_true',help='Resume this specialist run from its own last.pt checkpoint.')
    args=parser.parse_args()
    if not 60<=args.epochs<=100:parser.error('Use 60–100 maximum epochs with early stopping.')
    tempfile.tempdir=str(ROOT/'training')
    import torch
    torch.set_num_threads(4)
    from ultralytics import YOLO
    gpu=torch.cuda.is_available()
    if not gpu and not args.allow_cpu:raise SystemExit('CPU-only training can take many hours. Not started without --allow-cpu.')
    dataset=ROOT/'dataset-pothole-specialist';assert (dataset/'preparation-report.json').exists(),'Prepare and validate dataset first'
    # Relocatable config generated for this machine; approved V2 config is never changed.
    config=dataset/'dataset.yaml';config.write_text('path: '+dataset.as_posix()+'\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 1\nnames:\n  0: pothole\n')
    checkpoint=ROOT/'training/pretrained/yolo11n.pt'
    import hashlib
    assert hashlib.file_digest(checkpoint.open('rb'),'sha256').hexdigest()=='0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1','Pretrained checkpoint hash mismatch'
    prior_seconds=0.
    if args.resume:
        run=ROOT/'training/runs/pothole-specialist'/f'nano-{args.imgsz}'
        checkpoint=run/'weights/last.pt'
        assert checkpoint.is_file(),'No specialist checkpoint to resume'
        assert not (run/'training-report.json').exists(),'Completed training must not be resumed'
        import csv
        rows=list(csv.DictReader((run/'results.csv').open()))
        resume_from_epoch=int(rows[-1]['epoch']) if rows else 0
        prior_status=json.loads((ROOT/'training/pothole-specialist-status.json').read_text())
        prior_seconds=float(rows[-1]['time']) if rows else 0.
        if prior_status.get('resumed'):
            earlier=float(prior_status.get('prior_completed_training_seconds',0))
            prior_seconds=earlier+(prior_seconds if resume_from_epoch>prior_status.get('resume_from_epoch',3) else 0.)
    start=time.perf_counter();model=YOLO(str(checkpoint))
    status=ROOT/'training/pothole-specialist-status.json'
    status.write_text(json.dumps({'status':'training','device':'cuda' if gpu else 'cpu',
        'epochs_maximum':args.epochs,'imgsz':args.imgsz,'started_unix':time.time(),
        'active_model_unchanged':True,'accepted':False,'resumed':args.resume,
        'resume_from_epoch':resume_from_epoch if args.resume else 0,
        'prior_completed_training_seconds':prior_seconds},indent=2))
    print('Starting real one-class pothole training:',args.epochs,'maximum epochs;', 'CUDA' if gpu else 'CPU',flush=True)
    if args.resume:
        model.train(resume=True,device=0 if gpu else 'cpu',workers=0)
    else:
        model.train(data=str(config),epochs=args.epochs,imgsz=args.imgsz,batch=-1 if gpu else 8,
        patience=15,device=0 if gpu else 'cpu',workers=0,seed=42,pretrained=True,
        project=str(ROOT/'training/runs/pothole-specialist'),name=f'nano-{args.imgsz}',exist_ok=False,
        mosaic=.5,close_mosaic=15,translate=.1,scale=.3,fliplr=.5,flipud=0,cos_lr=True,plots=True)
    best=Path(model.trainer.best);candidate=YOLO(str(best))
    validation=candidate.val(data=str(config),split='val',imgsz=args.imgsz,plots=True)
    test=candidate.val(data=str(config),split='test',imgsz=args.imgsz,plots=True)
    # Static ONNX at the runtime's 640 input; test this exported file independently.
    exported=candidate.export(format='onnx',imgsz=640,batch=1,dynamic=False,half=False,simplify=False,nms=False,opset=17)
    report={'training_seconds':prior_seconds+time.perf_counter()-start,'best_pt':str(best),'candidate_onnx':str(exported),
        'validation':validation.results_dict,'test':test.results_dict,'deployed':False,
        'next_gate':'Independent ONNX test on original scenes and negatives, then visual review; never deploy from training metrics alone.',
        'licensing':'Ultralytics code/weights use AGPL-3.0 terms; retained dataset source attribution and CC BY-SA requirements apply. See dataset licenses.'}
    (best.parent.parent/'training-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
    status.write_text(json.dumps({'status':'trained_candidate_requires_acceptance',**report},indent=2))
if __name__=='__main__':main()
