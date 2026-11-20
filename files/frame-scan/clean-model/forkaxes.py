import trimesh,numpy as np,json
m=trimesh.load('fill2.stl')
def circ(p):
  A=np.c_[2*p,np.ones(len(p))]; b=(p**2).sum(1); q=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(q[2]+q[:2]@q[:2]); return q[:2],r,np.abs(np.linalg.norm(p-q[:2],axis=1)-r)
d=np.array([-0.0445,0.4247,0.9043]);d/=np.linalg.norm(d); c0=np.array([-11.0,74.8,166.7])
C={'L':[],'R':[]}
for h in np.arange(-430,40,5):
  o=c0+h*d; s=m.section(plane_origin=o,plane_normal=d)
  if s is None: continue
  p2,T=s.to_2D()
  for e in p2.discrete:
    if len(e)<8: continue
    c,r,res=circ(e); c3=trimesh.transform_points([[c[0],c[1],0]],T)[0]
    if abs(c3[0]+11)>70 and abs(c3[0]+11)<120 and res.mean()<2.6 and 13<r<20 and c3[1]<150: C['L' if c3[0]<-11 else 'R'].append(c3)
out={}
for k,P in C.items():
  P=np.array(P); cm=P.mean(0); v=np.linalg.svd(P-cm)[2][0]; v*=np.sign(v[2]); res=np.linalg.norm(np.cross(P-cm,v),axis=1)
  keep=res<2*np.median(res)+1; P=P[keep]; cm=P.mean(0); v=np.linalg.svd(P-cm)[2][0]; v*=np.sign(v[2]); res=np.linalg.norm(np.cross(P-cm,v),axis=1)
  print(k,len(P),'pt',np.round(cm,1),'dir',np.round(v,4),'rake',round(np.degrees(np.arctan2(v[1],v[2])),2),'lean',round(np.degrees(np.arctan2(v[0],v[2])),2),'res rms',round(np.sqrt((res**2).mean()),2),'z',round(P[:,2].min()),round(P[:,2].max()))
  out[k]=dict(pt=cm.tolist(),dir=v.tolist())
# c-c at z=0 plane
def atz(o,z):
  p=np.array(o['pt']);v=np.array(o['dir']);return p+(z-p[2])/v[2]*v
for z in (-150,0,150): a,b=atz(out['L'],z),atz(out['R'],z); print('z',z,'L',np.round(a,1),'R',np.round(b,1),'c-c',round(np.linalg.norm(a-b),1))
json.dump(out,open('forkaxes.json','w'))
