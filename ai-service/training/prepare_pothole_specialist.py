"""Create a separate, traceable one-class corpus. Never edit approved Dataset V2."""
import hashlib,json,math,shutil
from pathlib import Path
from collections import Counter,defaultdict
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'dataset-v2';TARGET=ROOT/'dataset-pothole-specialist'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    if TARGET.exists():raise SystemExit('Specialist dataset already exists; refusing to overwrite it.')
    records=json.loads((SOURCE/'manifest.json').read_text());manifest=[];groups=defaultdict(set);areas=[];crop_sizes=[]
    before={r['image']:digest(SOURCE/r['image']) for r in records}
    for split in ['train','val','test']:
        (TARGET/'images'/split).mkdir(parents=True);(TARGET/'labels'/split).mkdir(parents=True)
    for r in records:
        if not (0 in r['classes'] or not r['classes']):continue
        split=r['split'];groups[r['group']].add(split)
        source=SOURCE/r['image'];label=SOURCE/'labels'/split/source.with_suffix('.txt').name
        boxes=[]
        for line in label.read_text().splitlines():
            c,x,y,w,h=map(float,line.split())
            if int(c)==0:boxes.append((x-w/2,y-h/2,x+w/2,y+h/2));areas.append(w*h)
        im=Image.open(source).convert('RGB');W,H=im.size
        if 0 in r['classes'] and not boxes:raise ValueError('Positive without pothole box')
        dest=TARGET/'images'/split/source.name;shutil.copy2(source,dest)
        (TARGET/'labels'/split/source.with_suffix('.txt').name).write_text(''.join(
            f'0 {(a+c)/2:.8f} {(b+d)/2:.8f} {c-a:.8f} {d-b:.8f}\n' for a,b,c,d in boxes))
        manifest.append({**r,'parent_image':r['image'],'derivative':False,'classes':[0] if boxes else [],'sha256':digest(dest)})
        # Validation/test remain uncropped original scenes; training gets contextual derivatives only.
        if split!='train' or not boxes:continue
        largest=max(boxes,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));a,b,c,d=largest
        cx,cy=(a+c)*W/2,(b+d)*H/2;side=max((c-a)*W,(d-b)*H)
        prior_crops=set()
        for name,factor in [('tight',2),('medium',4),('road',7)]:
            length=max(96,side*factor);left=max(0,math.floor(cx-length/2));top=max(0,math.floor(cy-length/2))
            right=min(W,math.ceil(cx+length/2));bottom=min(H,math.ceil(cy+length/2))
            rectangle=(left,top,right,bottom)
            if rectangle in prior_crops or rectangle==(0,0,W,H):continue
            prior_crops.add(rectangle);cropped=im.crop(rectangle);new_boxes=[]
            for x1,y1,x2,y2 in boxes:
                X1,Y1,X2,Y2=x1*W,y1*H,x2*W,y2*H
                l,t,rr,bb=max(left,X1),max(top,Y1),min(right,X2),min(bottom,Y2)
                if rr<=l or bb<=t:continue
                # Reject crops cutting through an object: no unlabeled visible potholes.
                if (rr-l)*(bb-t)<.95*(X2-X1)*(Y2-Y1):new_boxes=[];break
                new_boxes.append(((l-left)/(right-left),(t-top)/(bottom-top),(rr-left)/(right-left),(bb-top)/(bottom-top)))
            if not new_boxes:continue
            filename=source.stem+'__'+name+'.jpg';dest=TARGET/'images/train'/filename;cropped.save(dest,quality=95)
            (TARGET/'labels/train'/Path(filename).with_suffix('.txt')).write_text(''.join(
                f'0 {(x1+x2)/2:.8f} {(y1+y2)/2:.8f} {x2-x1:.8f} {y2-y1:.8f}\n' for x1,y1,x2,y2 in new_boxes))
            manifest.append({**r,'image':'images/train/'+filename,'file':filename,'parent_image':r['image'],
                'derivative':True,'crop_pixels':rectangle,'classes':[0],'sha256':digest(dest)})
            crop_sizes.extend((x2-x1)*(y2-y1) for x1,y1,x2,y2 in new_boxes)
    assert not any(len(s)>1 for s in groups.values()),'Source group crosses splits'
    hashes=defaultdict(set)
    for r in manifest:
        hashes[r['sha256']].add(r['split']);p=TARGET/r['image']
        with Image.open(p) as im:im.verify()
        for line in (TARGET/'labels'/r['split']/p.with_suffix('.txt').name).read_text().splitlines():
            cls,x,y,w,h=map(float,line.split());assert cls==0 and 0<w<=1 and 0<h<=1 and 0<=x-w/2<=x+w/2<=1.000001 and 0<=y-h/2<=y+h/2<=1.000001
    assert not any(len(s)>1 for s in hashes.values()),'Exact cross-split duplicate'
    assert all(digest(SOURCE/r['image'])==before[r['image']] for r in records),'Approved V2 changed'
    near=json.loads((SOURCE/'near_duplicate_report.json').read_text())
    cross=[p for p in near['pairs'] if p['split_a']!=p['split_b'] and any(r['image']==p['image_a'] for r in manifest) and any(r['image']==p['image_b'] for r in manifest)]
    assert not cross,'Existing cross-split near duplicate'
    (TARGET/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (TARGET/'dataset.yaml').write_text('path: '+TARGET.as_posix()+'\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 1\nnames:\n  0: pothole\n')
    shutil.copytree(SOURCE/'licenses',TARGET/'licenses');shutil.copy2(SOURCE/'DATASET_SOURCES.md',TARGET/'DATASET_SOURCES.md')
    sorted_areas=sorted(areas);report={'source_real_positive_images':sum(0 in r['classes'] for r in records),
      'original_box_count':len(areas),'box_area_median_fraction':sorted_areas[len(areas)//2],
      'original_boxes_under_1_percent':sum(a<.01 for a in areas),
      'crop_box_area_median_fraction':sorted(crop_sizes)[len(crop_sizes)//2] if crop_sizes else None,
      'splits':{s:{'original_positive_images':sum(r['split']==s and not r['derivative'] and bool(r['classes']) for r in manifest),
        'original_negative_images':sum(r['split']==s and not r['classes'] for r in manifest),
        'training_derivatives':sum(r['split']==s and r['derivative'] for r in manifest),
        'images':sum(r['split']==s for r in manifest)} for s in ['train','val','test']},
      'validation_test_derivatives':0,'approved_v2_unchanged':True,'cross_split_exact_duplicates':0,
      'inherited_near_duplicate_cross_split_pairs':len(cross),
      'limitation':'Derivative-to-held-out perceptual similarity has not been exhaustively screened; parent groups and existing near-duplicate screen retained.',
      'diagnosis':'Small road-view boxes are a plausible failure contributor, not proven sole cause. Original test boxes and original scenes are retained for acceptance.'}
    (TARGET/'preparation-report.json').write_text(json.dumps(report,indent=2))
    examples=[r for r in manifest if r['derivative']][:24];sheet=Image.new('RGB',(1000,math.ceil(len(examples)/4)*220),'white');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(examples):
        im=Image.open(TARGET/r['image']).convert('RGB');im.thumbnail((245,185));d=ImageDraw.Draw(im)
        for line in (TARGET/'labels/train'/Path(r['image']).with_suffix('.txt').name).read_text().splitlines():
            _,x,y,w,h=map(float,line.split());d.rectangle(((x-w/2)*im.width,(y-h/2)*im.height,(x+w/2)*im.width,(y+h/2)*im.height),outline='red',width=2)
        pos=((i%4)*250,(i//4)*220);sheet.paste(im,pos);draw.text((pos[0],pos[1]+187),r['file'][-30:],fill='black')
    sheet.save(TARGET/'crop-review.jpg');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
