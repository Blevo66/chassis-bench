# Smooth rebuild of scan-derived parts: per-slice 2D signed distance -> mirror about X=0 -> 3D Gaussian -> contours -> spline loft
import trimesh,numpy as np,json,cadquery as cq,sys
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt,gaussian_filter
from skimage.measure import find_contours
V=lambda p:cq.Vector(*map(float,p))
m=trimesh.load('cad/frame-scan-watertight-bike-aligned.stl')
PX=0.5
def section_poly(o,n,e1,e2,clip):
  s=m.section(plane_origin=o,plane_normal=n)
  if s is None: return None
  ps=[Polygon(np.c_[(e-o)@e1,(e-o)@e2]).buffer(0) for e in s.discrete if len(e)>3]
  ps=[p for p in ps if p.area>20]
  if not ps: return None
  G=unary_union(ps).intersection(clip)
  return None if G.is_empty else G
def build(n,e1,e2,hs,clipfn,xa,yr,mirror,sig_xy=1.2,sig_h=1.0):
  xs=np.arange(-xa,xa+PX/2,PX); ys=np.arange(yr[0],yr[1],PX); X,Y=np.meshgrid(xs,ys,indexing='ij'); pts=np.c_[X.ravel(),Y.ravel()]
  vol=[]
  for h in hs:
    G=section_poly(h*n,n,e1,e2,clipfn(h)); inside=np.zeros(X.shape,bool)
    if G is not None:
      for g in ([G] if G.geom_type=='Polygon' else [g for g in getattr(G,'geoms',[]) if g.geom_type=='Polygon']):
        inside|=Path(np.array(g.exterior.coords)).contains_points(pts).reshape(X.shape)
    vol.append(distance_transform_edt(~inside)*PX-distance_transform_edt(inside)*PX)
  vol=np.array(vol)
  if mirror: vol=0.5*(vol+np.flip(vol,axis=1))
  vol=gaussian_filter(vol,(sig_h,sig_xy/PX,sig_xy/PX))
  return xs,ys,vol
def contours(xs,ys,d,minarea=25):
  out=[]
  for c in find_contours(d,0.0):
    if len(c)<10 or np.linalg.norm(c[0]-c[-1])>1e-6: continue
    P=np.c_[np.interp(c[:,0],np.arange(len(xs)),xs),np.interp(c[:,1],np.arange(len(ys)),ys)]
    pg=Polygon(P)
    if pg.is_valid and pg.area>minarea: out.append(pg)
  return out
def resample(poly,N):
  xy=np.array(poly.exterior.coords)[:-1]
  if not Polygon(xy).exterior.is_ccw: xy=xy[::-1]
  c=np.array(poly.centroid.coords[0])
  ang=np.arctan2(xy[:,0]-c[0],-(xy[:,1]-c[1]))   # start at the point straight 'below/front' of centroid
  i0=np.argmin(np.abs(ang)); xy=np.roll(xy,-i0,axis=0); xy=np.vstack([xy,xy[:1]])
  L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]; t=np.linspace(0,L[-1],N+1)[:-1]
  return np.c_[np.interp(t,L,xy[:,0]),np.interp(t,L,xy[:,1])]
def wire(xy,o,e1,e2):
  pts=[V(o+x*e1+y*e2) for x,y in xy]
  return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts,periodic=True)])
def loft_group(xs,ys,vol,hs,n,e1,e2,sel,every=2,N=64):
  ws=[]; used=[]
  for i in range(0,len(hs),every):
    cs=[c for c in contours(xs,ys,vol[i]) if sel(c)]
    if not cs: continue
    c=max(cs,key=lambda p:p.area); ws.append(wire(resample(c,N),hs[i]*n,e1,e2)); used.append(hs[i])
  if (len(hs)-1)%every:
    cs=[c for c in contours(xs,ys,vol[-1]) if sel(c)]
    if cs: ws.append(wire(resample(max(cs,key=lambda p:p.area),N),hs[-1]*n,e1,e2)); used.append(hs[-1])
  sol=cq.Solid.makeLoft(ws,False)
  # cap: makeLoft closes ends with planar faces
  return sol,used
X=np.array([1.,0,0]); Y=np.array([0,1.,0]); Z=np.array([0,0,1.])
vb=np.array([0,0.4283,0.9036]); vb/=np.linalg.norm(vb); ey=np.cross(vb,X)
out={}
which=sys.argv[1:] or ['gusset','junction','ybot','ytop']
if 'gusset' in which:
  def gclip(z):
    ya=0.474*z
    y0=ya if z>=4 else max(ya+25,25)
    xl=26.5 if 2<=z<=40 else 45
    return box(-xl,y0,xl,128)
  hs=np.arange(-136,104,2.0)
  xs,ys,vol=build(Z,X,Y,hs,gclip,48,(-30,140),True)
  out['gusset'],u=loft_group(xs,ys,vol,hs,Z,X,Y,lambda c:True,every=3)
if 'junction' in which:
  hs=np.arange(311,452,2.0)
  xs,ys,vol=build(Y,X,Z,hs,lambda y:box(-38,-140,38,20),40,(-145,25),False)
  out['junction'],u=loft_group(xs,ys,vol,hs,Y,X,Z,lambda c:True,every=3)
if 'ybot' in which:
  hs=np.arange(-34,-2,1.0)
  xs,ys,vol=build(vb,X,ey,hs,lambda h:box(-150,-90,150,45),150,(-95,50),True,sig_h=1.5)
  a,_=loft_group(xs,ys,vol,hs,vb,X,ey,lambda c:True,every=3)
  hs=np.arange(-5,10,1.0)
  xs,ys,vol=build(vb,X,ey,hs,lambda h:box(-60,-60,60,28),62,(-62,30),True,sig_h=1.5)
  b,_=loft_group(xs,ys,vol,hs,vb,X,ey,lambda c:abs(c.centroid.x)<20,every=3)
  out['ybot']=a.fuse(b).clean()
if 'ytop' in which:
  hs=np.arange(172,214,1.0)
  xs,ys,vol=build(vb,X,ey,hs,lambda h:box(-150,-90,150,45),150,(-95,50),True,sig_h=1.0)
  plate_i=(hs>=184)&(hs<=207)
  p,_=loft_group(xs,ys,vol[plate_i],hs[plate_i],vb,X,ey,lambda c:c.area>5000,every=3)
  parts=[p]
  for side in (-1,1):
    sel=lambda c,s=side:(c.centroid.x*s>40)
    for lo,hi in ((172,186),(205,214)):
      ii=(hs>=lo)&(hs<=hi)
      cs0=[c for c in contours(xs,ys,vol[ii][0]) if sel(c)]
      try:
        q,_=loft_group(xs,ys,vol[ii],hs[ii],vb,X,ey,sel,every=2); parts.append(q)
      except Exception as e: print('clamp loft fail',side,lo,e)
  # risers
  hs2=np.arange(212,236,1.0)
  xs2,ys2,vol2=build(vb,X,ey,hs2,lambda h:box(-75,-40,75,40),76,(-42,42),True)
  for side in (-1,1):
    try:
      q,_=loft_group(xs2,ys2,vol2,hs2,vb,X,ey,lambda c,s=side:c.centroid.x*s>15,every=3); parts.append(q)
    except Exception as e: print('riser fail',e)
  t=parts[0]
  for q in parts[1:]: t=t.fuse(q)
  out['ytop']=t.clean()
for k,s in out.items():
  bb=s.BoundingBox(); print(k,s.isValid(),round(s.Volume()),[round(x) for x in (bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax)])
  s.exportBrep(f'cad/smooth-{k}.brep')
  cq.exporters.export(cq.Workplane().add(s),f'cad/smooth-{k}.stl',tolerance=0.2,angularTolerance=0.3)
