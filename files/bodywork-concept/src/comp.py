import sys,numpy as np
from PIL import Image,ImageDraw,ImageFilter
photo,paint,out,polys=sys.argv[1],sys.argv[2],sys.argv[3],eval(sys.argv[4])
ph=Image.open(photo).convert('RGB'); base=ph.copy()
pt=Image.open(paint).convert('RGBA').filter(ImageFilter.GaussianBlur(0.6))
a=np.asarray(pt).astype(np.float32); a[...,:3]=np.clip(a[...,:3]*np.array([1,.985,.95])+np.random.default_rng(1).normal(0,4,a[...,:3].shape),0,255)
pt=Image.fromarray(a.astype(np.uint8),'RGBA'); base.paste(pt,(0,0),pt)
m=Image.new('L',ph.size,0); d=ImageDraw.Draw(m)
for p in polys: d.polygon(p,fill=255)
base.paste(ph,(0,0),m.filter(ImageFilter.GaussianBlur(1.2)))
base.save(out,quality=90)
