import trimesh,numpy as np,json,cadquery as cq
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from scipy.interpolate import splprep,splev
V=lambda p:cq.Vector(*map(float,p))
M=np.array(json.load(open('cad/transform.json'))['scan_to_bike'])
m=trimesh.load('cad/frame-scan-watertight-bike-aligned.stl')
vb=np.array([0,0.4283,0.9036]);vb/=np.linalg.norm(vb); ex=np.array([1.,0,0]); ey=np.cross(vb,ex)
def layer_polys(h,clip):
  o=h*vb; s=m.section(plane_origin=o,plane_normal=vb)
  if s is None: return []
  ps=[]
  for e in s.discrete:
    if len(e)<4: continue
    p=Polygon(np.c_[(e-o)@ex,(e-o)@ey]).buffer(0)
    if p.area>30: ps.append(p)
  G=unary_union(ps).intersection(clip)
  gs=[G] if G.geom_type=='Polygon' else [g for g in getattr(G,'geoms',[]) if g.geom_type=='Polygon']
  return [Polygon(g.exterior).simplify(0.4) for g in gs if g.area>40]
def stack(h0,h1,step,clip):
  body=None; info=[]
  for h in np.arange(h0,h1,step):
    for g in layer_polys(h+step/2,clip):
      pts=[V(x*ex+y*ey+h*vb) for x,y in list(g.exterior.coords)[:-1]]
      w=cq.Wire.makePolygon(pts,close=True); f=cq.Face.makeFromWires(w)
      pr=cq.Solid.extrudeLinear(f,V(vb*step))
      body=pr if body is None else body.fuse(pr)
    info.append(h)
  return body.clean()
# bottom yoke: h -36..-3 full width, central boss -3..9 (front of frame only)
by=stack(-36,-3,2,box(-150,-80,150,45))
boss=stack(-3,9,2,box(-60,-60,60,28))
bottom=by.fuse(boss).clean()
# top yoke: clamps + plate h 172..214, bar-clamp risers 214..235
top=stack(172,214,2,box(-150,-80,150,40)).fuse(stack(214,235,2,box(-75,-40,75,40))).clean()
# handlebar: scanned centreline (skeleton) in scan coords -> bike frame, Ø22.2 (7/8in, assumed)
import pickle
segs=pickle.load(open('segs.pkl','rb'))
P=np.vstack([segs[4]['pts'],segs[24]['pts'],segs[3]['pts'][::-1]])
P=P[np.argsort(P[:,0])]
P=(np.c_[P,np.ones(len(P))]@M.T)[:,:3]
L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P,axis=0),axis=1))]
tck,_=splprep(P.T,u=L/L[-1],s=len(P)*6); u=np.linspace(0,1,40)
C=np.array(splev(u,tck)).T; Tn=np.array(splev(u,tck,der=1)).T
bar=cq.Solid.makeLoft([cq.Wire.makeCircle(11.1,V(c),V(t/np.linalg.norm(t))) for c,t in zip(C,Tn)],False)
for k,s in (('bottom',bottom),('top',top),('bar',bar)):
  bb=s.BoundingBox(); print(k,s.isValid(),round(s.Volume()),[round(x) for x in (bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax)])
import pickle as pk
cq.exporters.export(cq.Workplane().add(bottom),'cad/yoke-bottom.stl',tolerance=0.1); cq.exporters.export(cq.Workplane().add(top),'cad/yoke-top.stl',tolerance=0.1); cq.exporters.export(cq.Workplane().add(bar),'cad/handlebar.stl',tolerance=0.1)
with open('cad/yokes.brep.pkl','wb') as f: pass
bottom.exportBrep('cad/yoke-bottom.brep'); top.exportBrep('cad/yoke-top.brep'); bar.exportBrep('cad/handlebar.brep')
