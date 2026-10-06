"""Independent ONNX acceptance test. Does not install or activate any candidate."""
import argparse,hashlib,json,sys
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from utils.pothole_onnx import PotholeDetector
from time import perf_counter
import numpy as np

def average_precision(predictions, ground_truth_count):
    """101-point interpolated detection AP at IoU .50:.05:.95, one class.

    Each row contains confidence and ten independent one-to-one match flags.
    Predictions must be collected at a low score threshold, not the operating
    confidence, otherwise low-recall points would be silently discarded.
    """
    if not predictions or not ground_truth_count:
        return [0.0]*10
    flags=np.asarray([row[1] for row in sorted(predictions,key=lambda row:-row[0])],dtype=float)
    tp=flags.cumsum(axis=0);fp=(1-flags).cumsum(axis=0)
    recall=tp/ground_truth_count;precision=tp/np.maximum(tp+fp,1e-12)
    aps=[]
    for k in range(10):
        r=recall[:,k];p=np.maximum.accumulate(precision[::-1,k])[::-1]
        # Unreached recall levels contribute zero; never interpolate a long
        # artificial tail between the last detection and recall 1.
        aps.append(float(np.mean([p[np.searchsorted(r,target,side='left')]
            if np.searchsorted(r,target,side='left') < len(p) else 0.
            for target in np.linspace(0,1,101)])))
    return aps
def overlap(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return inter/max(1e-9,(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter)
def main():
    p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--confidence',type=float,default=.35)
    p.add_argument('--split',choices=['val','test'],default='test');args=p.parse_args()
    detector=PotholeDetector(args.model,confidence=.001);detector.load();assert detector.model,detector.error
    data=ROOT/'dataset-pothole-specialist';rows=[r for r in json.loads((data/'manifest.json').read_text()) if r['split']==args.split]
    review_path=ROOT.parent/'reports/moving-scan/pothole-negative-review.json'
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    counts=Counter();categories=Counter();negative_categories=Counter();predictions=[];seconds=[];ap_predictions=[]
    sheet=Image.new('RGB',(1000,((len(rows)+3)//4)*220),'white');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(rows):
        image=Image.open(data/r['image']).convert('RGB');start=perf_counter();all_ds=detector.detect(image);seconds.append(perf_counter()-start)
        ds=[d for d in all_ds if d['confidence']>=args.confidence]
        gs=[]
        for line in (data/'labels'/args.split/Path(r['image']).with_suffix('.txt').name).read_text().splitlines():
            _,x,y,w,h=map(float,line.split());gs.append([x-w/2,y-h/2,x+w/2,y+h/2])
        ap_used=[set() for _ in range(10)]
        for detection in sorted(all_ds,key=lambda d:-d['confidence']):
            b=detection['bbox'];box=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']];flags=[]
            for k,threshold in enumerate(np.linspace(.5,.95,10)):
                candidates=[(overlap(box,g),j) for j,g in enumerate(gs) if j not in ap_used[k]]
                matched=bool(candidates and max(candidates)[0]>=threshold)
                if matched:ap_used[k].add(max(candidates)[1])
                flags.append(matched)
            ap_predictions.append((detection['confidence'],flags))
        used=set();tp=0
        for d in sorted(ds,key=lambda d:-d['confidence']):
            b=d['bbox'];box=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']]
            matches=[(overlap(box,g),j) for j,g in enumerate(gs) if j not in used]
            if matches and max(matches)[0]>=.5:used.add(max(matches)[1]);tp+=1
        counts.update(gt=len(gs),tp=tp,fp=len(ds)-tp,positive_images=int(bool(gs)),matched_positive_images=int(tp>0),negative_images=int(not gs),negative_fp_images=int(not gs and bool(ds)))
        if not gs:
            tags=review.get('reviewed_test_categories',{}).get(r['file'],r.get('categories',[]) or ['uncategorized'])
            negative_categories.update(tags)
            if ds:categories.update(tags)
        predictions.append({'image':r['image'],'detections':ds,'matched_boxes':tp})
        image.thumbnail((245,185));d=ImageDraw.Draw(image)
        for x1,y1,x2,y2 in gs:
            d.rectangle((x1*image.width,y1*image.height,x2*image.width,y2*image.height),outline='green',width=2)
        for detection in ds:
            b=detection['bbox'];x,y=b['x']*image.width,b['y']*image.height
            d.rectangle((x,y,x+b['width']*image.width,y+b['height']*image.height),outline='red',width=2)
        pos=((i%4)*250,(i//4)*220);sheet.paste(image,pos);draw.text((pos[0],pos[1]+187),r['file'][:28],fill='black')
        draw.text((pos[0],pos[1]+202),f'GT green {len(gs)} | prediction red {len(ds)} | matched {tp}',fill='black')
    recall=counts['tp']/max(1,counts['gt']);fpr=counts['negative_fp_images']/max(1,counts['negative_images'])
    aps=average_precision(ap_predictions,counts['gt'])
    report={'split':args.split,'confidence':args.confidence,'counts':dict(counts),'box_recall_iou50':recall,
        'precision_iou50':counts['tp']/max(1,counts['tp']+counts['fp']),
        'mAP50':aps[0],'mAP50_95':float(np.mean(aps)),'ap_by_iou':aps,
        'ap_score_floor':.001,'ap_method':'101-point precision-envelope interpolation, one-to-one IoU matching, one class',
        'negative_false_positive_image_rate':fpr,'average_inference_ms':1000*sum(seconds)/len(seconds),
        'negative_category_image_counts':dict(negative_categories),
        'false_positive_categories':dict(categories),'numeric_gate_passed':recall>=.6 and fpr<=.15,
        'manual_prediction_review_required':True,'accepted':False,'activated':False,
        'model_sha256':hashlib.file_digest(args.model.open('rb'),'sha256').hexdigest()}
    if args.split=='test':
        supplemental=[]
        for relative in review.get('supplemental_pothole_negatives',[]):
            image=Image.open(ROOT/'dataset-v2'/relative).convert('RGB');start=perf_counter()
            ds=[d for d in detector.detect(image) if d['confidence']>=args.confidence]
            supplemental.append({'image':relative,'categories':['wet_roads'],
                'detections':ds,'inference_ms':1000*(perf_counter()-start)})
        report['supplemental_wet_road_results']=supplemental
        report['supplemental_wet_road_false_positive_images']=sum(bool(r['detections']) for r in supplemental)
        report['supplemental_wet_road_note']=review.get('supplemental_note')
    out=args.model.parent/f'acceptance-{args.split}';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps(report,indent=2));(out/'predictions.json').write_text(json.dumps(predictions,indent=2));sheet.save(out/'predictions-review.jpg');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
