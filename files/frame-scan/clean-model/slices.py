import trimesh,numpy as np,json
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
m=trimesh.load('fill2.stl')
def resample(poly,N,ref_dir):
  p=poly.exterior
  if not poly.exterior.is_ccw: p=Polygon(list(p.coords)[::-1]).exterior
  xy=np.array(p.coords)[:-1]; c=np.array(poly.centroid.coords[0])
  ang=np.arctan2(*(xy-c)[:,::-1].T); i0=np.argmin(np.abs(((ang-ref_dir)+np.pi)%(2*np.pi)-np.pi))
  xy=np.roll(xy,-i0,axis=0); xy=np.vstack([xy,xy[:1]])
  L=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]; t=np.linspace(0,L[-1],N+1)[:-1]
  return np.c_[np.interp(t,L,xy[:,0]),np.interp(t,L,xy[:,1])]
def stack(axis,vals,clipfn,N=72,simplify=0.6):
  out=[]
  for v in vals:
    o=[0,0,0];o[axis]=v; n=[0,0,0];n[axis]=1
    s=m.section(plane_origin=o,plane_normal=n)
    if s is None: continue
    P=s.discrete
    # build polygons in the two remaining axes
    ia=[i for i in range(3) if i!=axis]
    polys=[Polygon(e[:,ia]) for e in P if len(e)>3]
    polys=[p.buffer(0) for p in polys if p.is_valid or p.buffer(0).area>0]
    U=unary_union(polys)
    clip=clipfn(v)
    G=U.intersection(clip)
    if G.is_empty: continue
    geoms=[G] if G.geom_type=='Polygon' else list(G.geoms)
    geoms=[g for g in geoms if g.geom_type=='Polygon']
    if not geoms: continue
    g=max(geoms,key=lambda g:g.area); g=Polygon(g.exterior).simplify(simplify)
    xy=resample(g,N,0.0)
    pts=np.zeros((N,3)); pts[:,ia[0]]=xy[:,0]; pts[:,ia[1]]=xy[:,1]; pts[:,axis]=v
    out.append(dict(v=float(v),pts=pts.tolist(),area=g.area))
  return out
d=np.array([-0.0445,0.4247,0.9043]);d/=np.linalg.norm(d); c0=np.array([-11.0,74.8,166.7])
axy=lambda z: c0[1]+(z-c0[2])/d[2]*d[1]
# head gusset: z-slices, X-Y polygons, y from steering axis to 145, x within frame width (bosses clipped)
def hclip(z):
  xl,xr=(-37.5,15.5) if 40<=z<=75 else (-60,40)
  y0=max(axy(z),-10) if z>=44 else max(axy(z)+25,35)
  return box(xl,y0,xr,145)
head=stack(2,np.arange(-100,141,4),hclip)
# rear junction: y-slices, X-Z polygons
def rclip(y): return box(-75,-95,35,45)
rear=stack(1,np.arange(330,468,4),rclip)
json.dump(dict(head=head,rear=rear),open('slices.json','w'))
for k,S in (('head',head),('rear',rear)):
  print(k,len(S),[ (round(s['v']),round(s['area'])) for s in S][::4])
