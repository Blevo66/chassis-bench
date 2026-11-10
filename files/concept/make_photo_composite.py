import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ph=Image.open('../photo.jpg').convert('RGB'); P=np.asarray(ph).astype(np.float32)
H,W=P.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
out=P.copy()
# 1) blue shock spring -> XR yellow (only the fitted shock region)
r,g,b=P[...,0],P[...,1],P[...,2]
box=(xx>1060)&(xx<1310)&(yy>820)&(yy<1080)
blue=box&(b>r+25)&(b>g+10)
lum=(0.3*r+0.59*g+0.11*b)
k=np.clip((b-r)/80,0,1)[...,None]
yel=np.stack([np.clip(lum*2.3+40,0,255),np.clip(lum*1.9+25,0,255),np.clip(lum*0.35,0,255)],-1)
m=blue[...,None]*k
out=out*(1-m)+yel*m
# 2) rear rim silver -> gold (annulus)
cx,cy,rx,ry=685,1338,292,244
d=np.sqrt(((xx-cx)/rx)**2+((yy-cy)/ry)**2)
ann=(d>0.93)&(d<1.045)
sat=P.max(-1)-P.min(-1)
rim=ann&(sat<45)&(lum>70)
gold=np.stack([lum*1.05+30,lum*0.82+12,lum*0.30],-1).clip(0,255)
mm=Image.fromarray((rim*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
mm=np.asarray(mm)[...,None]/255.0
pass  # rim recolour dropped
base=Image.fromarray(out.clip(0,255).astype(np.uint8))
# 3) painted bodywork with grain
pt=Image.open('paint.png').convert('RGBA').filter(ImageFilter.GaussianBlur(0.7))
a=np.asarray(pt).astype(np.float32)
noise=np.random.default_rng(1).normal(0,5,a[...,:3].shape)
a[...,:3]=np.clip(a[...,:3]*np.array([1.0,0.985,0.95])+noise,0,255)  # warm it to the shed light
pt=Image.fromarray(a.astype(np.uint8),'RGBA')
base.paste(pt,(0,0),pt)
# 4) re-paste near fork leg + top yoke + near bar from the original photo
mask=Image.new('L',(W,H),0); dr=ImageDraw.Draw(mask)
dr.polygon([(1797,455),(1843,436),(2002,958),(2018,968),(2154,1338),(2098,1358),(1952,975),(1950,960)],fill=255)
dr.polygon([(1650,300),(1700,290),(1735,330),(1745,450),(1660,470),(1640,380)],fill=0)
mask=mask.filter(ImageFilter.GaussianBlur(1.2))
base.paste(ph,(0,0),mask)
base.save('photo-concept.png'); base.convert('RGB').save('photo-concept.jpg',quality=90)
base.resize((1288,966)).save('pc_s.jpg',quality=85)
base.crop((1000,300,2300,1300)).resize((1040,800)).save('pc_zoom.jpg',quality=85)
