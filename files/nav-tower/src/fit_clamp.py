import numpy as np,trimesh,sys,json
from scipy.spatial import cKDTree
exec(open('build_v1.py').read().split('parts={}')[0])
t0=float(sys.argv[1]) if len(sys.argv)>1 else 66.5
m=trimesh.load('clamp_raw.stl')
C2L=lambda P:np.c_[-P[:,0],P[:,2],P[:,1]+t0]
clamp=trimesh.Trimesh(L2S(C2L(m.vertices)),m.faces[:,::-1])
# U-bolt M10, 55 ID: legs through holes (±32.5,111.17,-6.2) dir back (0,.469,.883)
db=np.array([0,.469,.883]);db/=np.linalg.norm(db)
P0=np.array([0,111.17,-6.2]);sc=7.8;Rc=32.5
bc=P0+sc*db; e1=np.array([1.,0,0]); e2=db
arc=[bc+Rc*(np.cos(a)*e1+np.sin(a)*e2) for a in np.radians(np.linspace(0,180,19))]
fr=-30  # leg front end, s from P0 (forward is negative s)
legR=[np.array([32.5,0,0])+P0+s*db for s in np.linspace(fr,sc,5)]
legL=[np.array([-32.5,0,0])+P0+s*db for s in np.linspace(sc,fr,5)]
path=np.array(legR[:-1]+arc+legL[1:])
path_s=L2S(C2L(path))
segs=[trimesh.creation.cylinder(radius=5,segment=[p,q],sections=12) for p,q in zip(path_s[:-1],path_s[1:])]
# nuts on front face: find where the leg exits the clamp front (Z min along leg)
ub=trimesh.util.concatenate(segs)
# nut: 17AF x 8 placed at clamp exit; approximate exit s by ray test
nuts=[]
for sx in(1,-1):
  o=np.array([sx*32.5,0,0])+P0
  ss=np.linspace(0,-40,400);pts=L2S(C2L(np.array([o+s*db for s in ss])))
  inside=clamp.contains(pts) if clamp.is_watertight else None
  nuts.append(o)
parts={'clamp':clamp,'ubolt_M10_55ID':ub}
sw=np.load('sw45.npy');Pf=L2S(np.load('Pf.npy'));Pr=np.load('Pr.npy')
Ksw=cKDTree(L2S(sw));Ksw36=cKDTree(L2S(sw[np.hypot(sw[:,0],sw[:,1])>=36]));Kf=cKDTree(Pf)
rep={}
for k,mm in parts.items():
  pts,_=trimesh.sample.sample_surface_even(mm,20000);pts=np.vstack([pts,mm.vertices])
  d1,i1=Ksw.query(pts);d2,_=Ksw36.query(pts);d3,_=Kf.query(pts)
  j=d1.argmin();rep[k]=dict(sweep_all=round(float(d1.min()),1),at_local=S2L(pts[j:j+1])[0].round(0).tolist(),sweep_r36=round(float(d2.min()),1),frame=round(float(d3.min()),1))
  print(k,rep[k])
# where along the leg does the clamp end (front face) -> leg exit: sample clamp along leg line by nearest distance
for s in range(0,-40,-2):
  p=L2S(C2L((np.array([32.5,0,0])+P0+s*db)[None]))
  dd=trimesh.proximity.signed_distance(clamp,p)[0]
  if dd<0: print('leg exits clamp front at s',s,'clamp-coords',(np.array([32.5,0,0])+P0+s*db).round(1));break
import pickle;pickle.dump(parts,open('clamp_parts.pkl','wb'))
print('clamp local t range',C2L(m.vertices)[:,2].min().round(1),C2L(m.vertices)[:,2].max().round(1))
