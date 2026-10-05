"""Rasterize the existing CivicEye SVG eye geometry with supersampled Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
target = root / 'dist/icons'
target.mkdir(exist_ok=True)
# Absolute cubic control points from dist/favicon.svg; no new/placeholder logo.
curves = [((6,20),(6,20),(12,10),(20,10)),
          ((20,10),(28,10),(34,20),(34,20)),
          ((34,20),(34,20),(28,30),(20,30)),
          ((20,30),(12,30),(6,20),(6,20))]
for size in (192,512):
    for maskable in (False,True):
        scale = size * 4 / 40
        image = Image.new('RGB',(size*4,size*4),'#112d45')
        draw = ImageDraw.Draw(image)
        factor = .78 if maskable else 1
        def point(x,y): return ((20+(x-20)*factor)*scale,(20+(y-20)*factor)*scale)
        points=[]
        for curve in curves:
            for step in range(81):
                t=step/80; a=1-t
                x=a**3*curve[0][0]+3*a*a*t*curve[1][0]+3*a*t*t*curve[2][0]+t**3*curve[3][0]
                y=a**3*curve[0][1]+3*a*a*t*curve[1][1]+3*a*t*t*curve[2][1]+t**3*curve[3][1]
                points.append(point(x,y))
        draw.line(points,fill='#4de0bd',width=round(3*factor*scale),joint='curve')
        radius=1.5*factor*scale
        for x,y in points:
            draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill='#4de0bd')
        draw.ellipse((*point(15,15),*point(25,25)),fill='#4de0bd')
        name=f'{"maskable" if maskable else "icon"}-{size}.png'
        image.resize((size,size),Image.Resampling.LANCZOS).save(target/name)
print('Generated four branded Android icons from the existing eye geometry.')
