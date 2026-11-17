import numpy as np,trimesh,json
from scipy.spatial import cKDTree
p0=np.load('p0.npy');d=np.array([0,0.4705,0.8824]);d/=np.linalg.norm(d);n=np.array([0,d[2],-d[1]]);ex=np.array([1.,0,0]);R=np.stack([ex,n,d])
L2S=lambda P:p0+np.asarray(P,float)@R      # local (v,u,t) -> scan
S2L=lambda P:(np.asarray(P,float)-p0)@R.T
parts={};pieces={};import sys;BOLTS_=eval(sys.argv[1]) if len(sys.argv)>1 else [(150,145),(190,110)]
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
neck=[[s*17,u,t] for s in(1,-1) for u in(-36,-150) for t in(76,164)]
hull(neck,'neck')
ang=np.radians(np.linspace(-90,90,13))
br=[]
for r in(31,37):
  for a in ang:
    for t in(70,168): br.append([r*np.sin(a),-r*np.cos(a),t])
bp=[]
for a0,a1 in zip(ang[:-1],ang[1:]):
  q=[[r*np.sin(a),-r*np.cos(a),t] for r in(31,37) for a in(a0,a1) for t in(70,168)];bp.append(trimesh.convex.convex_hull(L2S(q)))
parts['bridge']=trimesh.util.concatenate(bp);pieces['bridge']=bp
# ---- side clamp plates (3 mm steel, joggled): front section at |v| 30-33 beside head tube, rear section at 24-27 on gusset
for s,nm in((1,'plate_R'),(-1,'plate_L')):
  front=[[s*v,u,t] for v in(29,32) for (u,t) in[(-30,70),(30,70),(30,168),(-30,168)]]
  rear=[[s*v,u,t] for v in(29,32) for (u,t) in[(40,72),(120,62),(170,86),(205,125),(205,158),(100,170),(40,170)]]
  jog=[[s*v,u,t] for v in(29,32) for (u,t) in[(30,70),(40,70),(40,168),(30,168)]]
  ms=[trimesh.convex.convex_hull(L2S(front)),trimesh.convex.convex_hull(L2S(jog)),
      trimesh.convex.convex_hull(L2S(rear[:8])),trimesh.convex.convex_hull(L2S(rear))]
  parts[nm]=trimesh.util.concatenate(ms);pieces[nm]=ms
# ---- through bolts in frame window (M8) local
BOLTS=BOLTS_
for i,(u,t) in enumerate(BOLTS):
  c=trimesh.creation.cylinder(radius=6,segment=[L2S([-30,u,t]),L2S([30,u,t])]);parts[f'bolt{i+1}']=c
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
json.dump(dict(clearance_at_45deg_lock=rep,bolts_local=BOLTS),open('clear.json','w'),indent=1)
import pickle;pickle.dump(parts,open('parts.pkl','wb'))
