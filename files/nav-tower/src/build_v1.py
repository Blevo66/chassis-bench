import numpy as np,trimesh,json
from scipy.spatial import cKDTree
p0=np.load('p0.npy');d=np.array([0,0.4705,0.8824]);d/=np.linalg.norm(d);n=np.array([0,d[2],-d[1]]);ex=np.array([1.,0,0]);R=np.stack([ex,n,d])
L2S=lambda P:p0+np.asarray(P,float)@R      # local (v,u,t) -> scan
S2L=lambda P:(np.asarray(P,float)-p0)@R.T
parts={};pieces={};import sys;UB_=eval(sys.argv[1]) if len(sys.argv)>1 else (136,152)
def hull(pts_local,name):
  m=trimesh.convex.convex_hull(L2S(pts_local));parts[name]=m;return m
def mirror(pts):
  pts=np.array(pts,float);out=list(pts)
  for p in pts:
    if p[0]!=0:out.append([-p[0],p[1],p[2]])
  return out
# ---- tower shell (faceted, carbon) local coords v,u,t
TOWER=mirror([[42,-140,78],[60,-250,70],[85,-262,160],[92,-265,265],[90,-250,345],
              [97,-232,408],[97,-150,408],[70,-160,385],[50,-155,350],[50,-150,250],[0,-275,215],[0,-146,180]])
hull(TOWER,'tower_shell')
# ---- neck between yokes (forward-gap) and bridge round head-tube front
# ---- v1: saddle on head-tube front + 2 U-bolts round it, clamping back to bars in the frame window
ang=np.radians(np.linspace(-90,90,13))
bp=[]
for a0,a1 in zip(ang[:-1],ang[1:]):
  q=[[r*np.sin(a),-r*np.cos(a),t] for r in(29,34) for a in(a0,a1) for t in(71,165)];bp.append(trimesh.convex.convex_hull(L2S(q)))
parts['saddle']=trimesh.util.concatenate(bp);pieces['saddle']=bp
def ubolt(name,tf,tb,ub,R=38,rr=4):
  segs=[];pc=[]
  # semicircle in front, plane tilts from tf (at front) to tb (at u=ub)
  tt=lambda u: tf+(tb-tf)*(u+R)/(ub+R)
  th=np.radians(np.linspace(90,-90,19))
  path=[[R*np.sin(x),-R*np.cos(x),0] for x in th]
  path=[[p[0],p[1],tt(p[1])] for p in path]
  L=[[R,ub+18,tt(ub+18)]]+[[R,u,tt(u)] for u in np.linspace(ub,0,6)]
  path=L[:-1]+path+[[-p[0],p[1],p[2]] for p in L[::-1][1:]]
  path=np.array(path)
  for p,q in zip(path[:-1],path[1:]):
    c=trimesh.creation.cylinder(radius=rr,segment=[L2S(p),L2S(q)],sections=10);segs.append(c)
  parts[name]=trimesh.util.concatenate(segs);pieces[name]=segs
  bar=[[s*v,ub+du,tt(ub)+dt] for s in(1,) for v in(-48,48) for du in(-8,8) for dt in(-6,6)]
  parts[name+'_backbar']=trimesh.convex.convex_hull(L2S(bar))
UB=UB_
ubolt('ubolt_lower',74,86,UB[0]);ubolt('ubolt_upper',160,130,UB[1])
neck=[[s*17,u,t] for s in(1,-1) for u in(-38,-150) for t in(86,150)]
parts['neck']=trimesh.convex.convex_hull(L2S(neck))
# ---- headlight 5" (guess: 140 OD rim, 75 deep), axis horizontal fwd (-Y scan), centre on front face
hc=L2S([0,-268,190]);hc=hc+np.array([0,10,0])
parts['headlight']=trimesh.creation.cylinder(radius=70,segment=[hc+[0,-8,0],hc+[0,67,0]])
# ---- 5" tablet (guess 145x80x14) on top deck facing rider, and 3" TFT dash (guess 80x58x14) in rear face
def panel(w,h,th,centre_local,tilt_deg):
  b=trimesh.creation.box([w,h,th]);  # in scan: x=lateral, y=height dir, z=normal
  a=np.radians(tilt_deg)  # face normal: backward (+Y) tilted up by a
  nrm=np.array([0,np.cos(a),np.sin(a)]);up=np.array([0,-np.sin(a),np.cos(a)])
  M=np.eye(4);M[:3,0]=[1,0,0];M[:3,1]=up;M[:3,2]=nrm;M[:3,3]=L2S(centre_local);b.apply_transform(M);return b
parts['tablet_5in']=panel(145,80,14,[0,-175,418],62)
parts['dash_3in_tft']=panel(80,58,14,[0,-150,330],25)
# ---- clearance check
sw=np.load('sw45.npy');Pf=np.load('Pf.npy')
Ksw=cKDTree(L2S(sw));Kf=cKDTree(L2S(Pf))
rep={}
for k,m in parts.items():
  pts,_=trimesh.sample.sample_surface_even(m,6000) if m.area>0 else (m.vertices,None)
  pts=np.vstack([pts,m.vertices])
  rep[k]=dict(steering_sweep_mm=round(float(Ksw.query(pts)[0].min()),1),frame_mm=round(float(Kf.query(pts)[0].min()),1))
  print(k,rep[k])
from scipy.spatial import Delaunay
Pf_s=L2S(Pf)
for k,m in parts.items():
  ps=pieces.get(k,[m]);ins=sum((Delaunay(p.vertices).find_simplex(Pf_s)>=0).sum() for p in ps)
  sws=sum((Delaunay(p.vertices).find_simplex(L2S(sw))>=0).sum() for p in ps)
  rep[k]['frame_pts_inside']=int(ins);rep[k]['sweep_pts_inside']=int(sws);print(k,'inside frame',ins,'inside sweep',sws)
  if ins or sws:
    for p in ps:
      for P,nm in((Pf_s,'frame'),(L2S(sw),'sweep')):
        h=P[Delaunay(p.vertices).find_simplex(P)>=0]
        if len(h): print('   ',nm,'hits local min',S2L(h).min(0).round(0),'max',S2L(h).max(0).round(0))
json.dump(dict(clearance_at_45deg_lock=rep,ubolt_bar_u=UB_),open('clear.json','w'),indent=1)
import pickle;pickle.dump(parts,open('parts.pkl','wb'))
