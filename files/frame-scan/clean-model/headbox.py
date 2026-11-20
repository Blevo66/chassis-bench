import trimesh,numpy as np,json
m=trimesh.load('fill2.stl')
d=np.array([-0.0445,0.4247,0.9043]);d/=np.linalg.norm(d);c0=np.array([-11.0,74.8,166.7])
axy=lambda z: c0[1]+(z-c0[2])/d[2]*d[1]
rows=[]
for z in np.arange(-100,186,5.0):
  s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
  if s is None: continue
  P=np.vstack(s.discrete)
  sel=P[(np.abs(P[:,0]+11)<45)&(P[:,1]>-10)&(P[:,1]<146)]
  if len(sel)<5: continue
  ya=axy(z)
  beh=sel[sel[:,1]>max(ya+26,sel[:,1].min())]
  if len(beh)<5: continue
  rows.append(dict(z=float(z),ymin=float(sel[:,1].min()),ymax=float(min(145,sel[:,1].max())),xmin=float(np.percentile(beh[:,0],1)),xmax=float(np.percentile(beh[:,0],99)),yaxis=float(ya)))
for r in rows: print({k:round(v,1) for k,v in r.items()})
json.dump(rows,open('headbox.json','w'))
# bosses
V=m.vertices
for side,sgn in (('L',-1),('R',1)):
  reg=V[(np.abs(V[:,1]-117)<16)&(np.abs(V[:,2]-61)<16)&((V[:,0]+11)*sgn>15)]
  tip=reg[np.argmax((reg[:,0]+11)*sgn)]
  print(side,'tip x',round(tip[0],1),'n',len(reg))
for x in (-46,-42,16,20):
  s=m.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
  for e in s.discrete:
    c=e.mean(0)
    if abs(c[1]-117)<15 and abs(c[2]-61)<15:
      p=e[:,1:]; A=np.c_[2*p,np.ones(len(p))]; b=(p**2).sum(1); q=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(q[2]+q[:2]@q[:2])
      print('boss slice x',x,'centre yz',np.round(q[:2],1),'D',round(2*r,1))
