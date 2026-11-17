import numpy as np
T=np.load('T.npy');rot=np.load('rot.npy');p0=np.load('p0.npy')
d=np.array([0,0.4705,0.8824]);d/=np.linalg.norm(d);n=np.array([0,d[2],-d[1]]);ex=np.array([1.,0,0])
R=np.stack([ex,n,d])  # rows: v,u,t
def samp(Tr,step=3):
  out=[]
  for k in range(Tr.shape[0]):
    a,b,c=Tr[k];m=int(max(np.linalg.norm(b-a),np.linalg.norm(c-a))/step)+1
    i,j=np.mgrid[0:m+1,0:m+1];msk=(i+j)<=m;i=i[msk]/m;j=j[msk]/m
    out.append(a+np.outer(i,b-a)+np.outer(j,c-a))
  return np.concatenate(out)
Pr=(samp(T[rot])-p0)@R.T; Pf=(samp(T[~rot])-p0)@R.T
np.save('Pr.npy',Pr);np.save('Pf.npy',Pf)
print(Pr.shape,Pf.shape)
