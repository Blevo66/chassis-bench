import trimesh,numpy as np,json
m=trimesh.load('fill2.stl')
F=json.load(open('forkaxes.json'));v=(np.array(F['L']['dir'])+np.array(F['R']['dir']));v/=np.linalg.norm(v)
c=np.array([-11.0,74.8,166.7])
def circ(p):
  A=np.c_[2*p,np.ones(len(p))]; b=(p**2).sum(1); q=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(q[2]+q[:2]@q[:2]); return q[:2],r,np.abs(np.linalg.norm(p-q[:2],axis=1)-r)
for it in range(3):
  cs=[];rows=[]
  for h in np.arange(-136,18,6):
    o=c+h*v; s=m.section(plane_origin=o,plane_normal=v)
    if s is None: continue
    p2,T=s.to_2D(); o2=trimesh.transform_points([o],np.linalg.inv(T))[0][:2]
    P=np.vstack(p2.discrete); rr=np.linalg.norm(P-o2,axis=1)
    # forward direction in 2D: project -Y
    f3=np.array([0,-1.0,0]); f3-= (f3@v)*v
    f2=trimesh.transform_points([o+f3],np.linalg.inv(T))[0][:2]-o2; f2/=np.linalg.norm(f2)
    sel=P[(rr>18)&(rr<32)&(((P-o2)@f2)>-5)]
    if len(sel)<10: continue
    cc,r,res=circ(sel)
    if 22<r<28 and res.mean()<1.2:
      cs.append(trimesh.transform_points([[cc[0],cc[1],0]],T)[0]); rows.append((h,round(2*r,1),round(res.mean(),2)))
  C=np.array(cs); cm=C.mean(0); c=cm
  print('iter',it,len(C),'centre',np.round(cm,1),'scatter rms',round(np.sqrt((np.linalg.norm(np.cross(C-cm,v),axis=1)**2).mean()),2))
print(rows)
# axis-to-fork distances (yoke offset)
for k in 'LR':
  p=np.array(F[k]['pt']); print(k,'dist to head axis',round(np.linalg.norm(np.cross(p-c,v)),1))
json.dump(dict(c=c.tolist(),v=v.tolist(),D=float(np.median([r[1] for r in rows]))),open('headaxis.json','w'))
