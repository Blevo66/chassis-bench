# Clean CAD rebuild of Joel's XL125R frame scan, in the scan's own coordinates (mm).
import json,numpy as np,cadquery as cq
from scipy.interpolate import splprep,splev
V=lambda p:cq.Vector(*map(float,p))
R=json.load(open('refine.json'))
# steering axis (fork-fitted direction, head-tube-fitted position)
d=np.array([-0.0445,0.4247,0.9043]);d/=np.linalg.norm(d)
c0=np.array([-11.0,74.8,166.7])
HT_BOT,HT_TOP,HT_OD=-138.0,19.0,50.0
def ok(name,lo=None,hi=None):
  P=[r['cen'] for r in R[name] if r['ok']]
  return np.array(P)
def smooth(P,n,s):
  L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
  tck,_=splprep(P.T,u=L/L[-1],s=s,k=3)
  u=np.linspace(0,1,n); return np.array(splev(u,tck)).T, np.array(splev(u,tck,der=1)).T
def frame(t):
  t=t/np.linalg.norm(t); X=np.array([1.,0,0]); lat=X-(X@t)*t; lat/=np.linalg.norm(lat); return t,lat
def tube(pts,w,h,n=9,s=None):
  pts=np.asarray(pts,float); s=len(pts)*4 if s is None else s
  P,T=smooth(pts,n,s)
  w=np.broadcast_to(np.interp(np.linspace(0,1,n),np.linspace(0,1,len(np.atleast_1d(w))),np.atleast_1d(w)),(n,))
  h=np.broadcast_to(np.interp(np.linspace(0,1,n),np.linspace(0,1,len(np.atleast_1d(h))),np.atleast_1d(h)),(n,))
  wires=[]
  for p,t,wi,hi in zip(P,T,w,h):
    t,lat=frame(t)
    if abs(wi-hi)<0.01: wires.append(cq.Wire.makeCircle(wi/2,V(p),V(t)))
    else:
      a,b=(hi/2,wi/2); up=np.cross(t,lat)
      wires.append(cq.Wire.makeEllipse(a,b,V(p),V(t),V(up)))  # major (h) along 'up'
  return cq.Solid.makeLoft(wires,False),P
parts={}
# head tube
parts['head_tube']=cq.Solid.makeCylinder(HT_OD/2,HT_TOP-HT_BOT,V(c0+HT_BOT*d),V(d))
ax=lambda h:c0+h*d
# backbone: from inside head tube, clean scan section, rear section near cut
bb=ok('backbone'); front=bb[(bb[:,1]>180)&(bb[:,1]<305)]; rear=bb[(bb[:,1]>425)&(bb[:,1]<460)]
bbpts=np.vstack([ax(-10),ax(-10)+np.array([0,40,-8]),front,[[-24,370,-8]],rear,[[-26,468,-50]]])
parts['backbone'],_=tube(bbpts,[45,45,45,45,48,51,51],[53,53,53,53,62,74,74],n=12,s=len(bbpts)*25)
# downtube Ø32
dt=ok('downtube'); dtc=dt[(dt[:,2]<-85)&(dt[:,2]>-255)]
dtpts=np.vstack([ax(-95),[[-10,108,-30]],dtc,[[-9,200,-312],[-9,218,-331]]])
parts['downtube'],_=tube(dtpts,32,32,n=10,s=len(dtpts)*6)
# brace (oval 22 wide x 32 tall)
br=ok('brace'); brc=br[(br[:,1]>158)&(br[:,1]<295)]
brpts=np.vstack([[[-11,128,-62]],brc,[[-24,335,8]]])
parts['brace'],_=tube(brpts,22,32,n=10,s=len(brpts)*3)
# rear rails as scanned (round, guessed Ø)
ra=ok('rearA'); rapts=np.vstack([[[-5,405,-42]],ra[::-1][1:]])
parts['rear_rail_right'],_=tube(rapts,20,20,n=8,s=len(rapts)*3)
rb=ok('rearB'); rbpts=np.vstack([[[-30,398,-30]],rb[:-4]])
parts['rear_rail_left'],_=tube(rbpts,22,22,n=8,s=len(rbpts)*3)
# head gusset web (simplified solid), profile in (y,z) at scan mid-plane, 44 wide
poly=[(55,125),(150,95),(150,45),(146,-40),(140,-75),(112,-92),(70,-20),(45,40)]
gus=(cq.Workplane(cq.Plane(origin=(-33,0,0),xDir=(0,1,0),normal=(1,0,0))).polyline(poly).close().extrude(44)).val()
parts['head_gusset']=gus
body=None
for k,s in parts.items():
  body=s if body is None else body.fuse(s)
body=body.clean()
# head tube bore: 47 x 15 bearing seats each end (26x47x15 taper), Ø40 between (guess)
bore=cq.Solid.makeCylinder(20,HT_TOP-HT_BOT+2,V(c0+(HT_BOT-1)*d),V(d))
for h0 in (HT_BOT-1,HT_TOP-14): bore=bore.fuse(cq.Solid.makeCylinder(23.5,15,V(c0+h0*d),V(d)))
body=body.cut(bore)
# steering axis datum stub not included; exported separately in README
cq.exporters.export(cq.Workplane().add(body),'cad/xl125r-frame-clean.step')
cq.exporters.export(cq.Workplane().add(body),'cad/xl125r-frame-clean.stl',tolerance=0.2,angularTolerance=0.2)
print('valid',body.isValid(),'volume',round(body.Volume()))
