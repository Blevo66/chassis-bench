import pickle,numpy as np,trimesh,json
from scipy.interpolate import splev
ch=pickle.load(open('chains.pkl','rb')); m=trimesh.load('fill2.stl')
def moments(xy):
  x,y=np.r_[xy[:,0],xy[0,0]],np.r_[xy[:,1],xy[0,1]]; x0,y0,x1,y1=x[:-1],y[:-1],x[1:],y[1:]
  cr=x0*y1-x1*y0; A=cr.sum()/2
  cx=((x0+x1)*cr).sum()/(6*A); cy=((y0+y1)*cr).sum()/(6*A)
  Ixx=((y0**2+y0*y1+y1**2)*cr).sum()/12; Iyy=((x0**2+x0*x1+x1**2)*cr).sum()/12; Ixy=((x0*y1+2*x0*y0+2*x1*y1+x1*y0)*cr).sum()/24
  C=np.array([[Iyy/A-cx**2,Ixy/A-cx*cy],[Ixy/A-cx*cy,Ixx/A-cy**2]]); return abs(A),np.array([cx,cy]),C
def station(c,t,maxoff=12):
  s=m.section(plane_origin=c,plane_normal=t)
  if s is None: return None
  p2,T=s.to_2D(); o2=trimesh.transform_points([c],np.linalg.inv(T))[0][:2]
  best=None
  for poly in p2.polygons_full:
    xy=np.array(poly.exterior.coords)[:-1]
    A,cen,C=moments(xy); dist=np.linalg.norm(cen-o2)
    if best is None or dist<best[0]: best=(dist,A,cen,C)
  if best is None or best[0]>maxoff: return None
  dist,A,cen,C=best; w,Vv=np.linalg.eigh(C); ax=4*np.sqrt(np.maximum(w,0))
  cen3=trimesh.transform_points([[cen[0],cen[1],0]],T)[0]
  maj3=trimesh.transform_points([[cen[0]+Vv[0,1],cen[1]+Vv[1,1],0]],T)[0]-cen3
  return dict(c=cen3.tolist(),A=A,dmin=float(ax[0]),dmaj=float(ax[1]),majdir=(maj3/np.linalg.norm(maj3)).tolist(),eqd=float(2*np.sqrt(A/np.pi)),off=float(dist))
out={}
for name in ['backbone','downtube','brace','rearA','rearB']:
  tck=ch[name]['tck']; rows=[]
  for u in np.linspace(0,1,81):
    c=np.array(splev(u,tck)); t=np.array(splev(u,tck,der=1)); t/=np.linalg.norm(t); r=None
    for it in range(3):
      r=station(c,t)
      if r is None: break
      c=np.array(r['c'])
    if r: r['u']=u; r['t']=t.tolist(); rows.append(r)
  out[name]=rows; print(name)
  for r in rows[::3]: print('  ',np.round(r['c']),'eqD',round(r['eqd'],1),'ell',round(r['dmaj'],1),'x',round(r['dmin'],1))
json.dump(out,open('refine2.json','w'))
