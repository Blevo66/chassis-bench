import numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
T=np.load('T.npy')
d=np.array([0,0.4705,0.8824]);d/=np.linalg.norm(d);n=np.array([0,d[2],-d[1]]);ex=np.array([1.,0,0])
p0=np.array([2.6,-33.8,0])+20*n
def loc(P):
  w=P-p0;return np.stack([w@ex,w@n,w@d],-1)  # v(lateral), u(back), t(along axis up)
C=loc(T.mean(1));v,u,t=C[...,0],C[...,1],C[...,2];r=np.hypot(v,u)
head=(r<34)&(t>50)&(t<185)
rot=((u<12)&~head)|((t>180)&(u<60))|((t<52)&(u<40)&(abs(v)<160)&~((r<34)&(t>50)))|(T.mean(1)[:,2]>255)
np.save('rot.npy',rot);np.save('p0.npy',p0)
L=np.array([0.3,-0.5,0.8]);L/=np.linalg.norm(L)
fig,ax=plt.subplots(1,2,figsize=(20,10))
for a,(i,j,k,s) in zip(ax,[(1,2,0,1),(0,2,1,-1)]):
  P=T;nrm=np.cross(P[:,1]-P[:,0],P[:,2]-P[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9
  sh=0.3+0.7*abs(nrm@L);o=np.argsort(s*P[:,:,k].mean(1))
  col=np.where(rot[o,None],np.c_[sh[o],sh[o]*.4,sh[o]*.4],np.c_[sh[o],sh[o],sh[o]])
  a.add_collection(PolyCollection(P[o][:,:,[i,j]],facecolors=col,edgecolors='none'));a.autoscale();a.set_aspect('equal')
ax[0].invert_xaxis();plt.tight_layout();plt.savefig('seg.png',dpi=55)
