# Pressed-steel backbone front + brace: scan sections, polar-resampled, mirrored about the seam, smoothed along the tube
import trimesh,numpy as np,json,cadquery as cq
from scipy.ndimage import uniform_filter1d
V=lambda p:cq.Vector(*map(float,p))
m=trimesh.load('cad/frame-scan-watertight-bike-aligned.stl')
RR=json.load(open('rrect.json'))
N=96; th=np.linspace(0,2*np.pi,N,endpoint=False)  # th=0 -> +up (seam top), clockwise to +X
def polar(e2,c2):
  d=e2-c2; ang=np.arctan2(d[:,0],d[:,1])%(2*np.pi); r=np.hypot(d[:,0],d[:,1])
  o=np.argsort(ang); ang,r=ang[o],r[o]
  ang=np.r_[ang-2*np.pi,ang,ang+2*np.pi]; r=np.r_[r,r,r]
  return np.interp(th,ang,r)
out={}
for name,rng in (('backbone',(150,302)),('brace',(140,292))):
  rows=[r for r in RR[name] if rng[0]<r['c'][1]<rng[1]]
  C=[];Tg=[];Rs=[];F=[]
  for r in rows:
    c=np.array(r['c']); t=np.array(r['t']); t/=np.linalg.norm(t)
    X3=np.array([1.,0,0]); X3-=(X3@t)*t; X3/=np.linalg.norm(X3); U3=np.cross(t,X3)
    s=m.section(plane_origin=c,plane_normal=t)
    best=None
    for e in s.discrete:
      lx=(e-c)@X3; lu=(e-c)@U3
      d=np.hypot(lx.mean(),lu.mean())
      if best is None or d<best[0]: best=(d,np.c_[lx,lu])
    e2=best[1]
    # area centroid
    x,y=e2[:,0],e2[:,1]; cr=x*np.roll(y,-1)-np.roll(x,-1)*y; A=cr.sum()/2
    c2=np.array([((x+np.roll(x,-1))*cr).sum()/(6*A),((y+np.roll(y,-1))*cr).sum()/(6*A)])
    rad=polar(e2,c2)
    rad=0.5*(rad+rad[(-np.arange(N))%N])   # mirror about the vertical seam line
    C.append(c+c2[0]*X3+c2[1]*U3); Tg.append(t); Rs.append(rad); F.append((X3,U3))
  C=np.array(C); Rs=np.array(Rs)
  C=uniform_filter1d(C,5,axis=0,mode='nearest'); Rs=uniform_filter1d(Rs,5,axis=0,mode='nearest')
  keep=np.r_[np.arange(0,len(C),2)] ; 
  if keep[-1]!=len(C)-1: keep=np.r_[keep,len(C)-1]
  wires=[]
  for i in keep:
    X3,U3=F[i]; pts=[C[i]+Rs[i,j]*(np.sin(th[j])*X3+np.cos(th[j])*U3) for j in range(N)]
    wires.append(cq.Wire.makePolygon([V(p) for p in pts],close=True))
  sol=cq.Solid.makeLoft(wires,True)
  # caps fine; report profile
  prof=Rs.mean(0); print(name,'stations',len(keep),'half-width at side',round(prof[N//4],1),'top ridge',round(prof[0],1),'bottom ridge',round(prof[N//2],1),'valid',sol.isValid())
  sol.exportBrep(f'cad/pressed-{name}.brep'); out[name]=sol
