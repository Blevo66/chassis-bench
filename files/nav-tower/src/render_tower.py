import numpy as np,trimesh,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
exec(open('tower.py').read().split("if __name__")[0])
T=np.load('T.npy');rot=np.load('rot.npy')
tw=trimesh.load('tower_plug.stl');trimesh.smoothing.filter_taubin(tw,iterations=12);tw.export('tower_plug_smooth.stl')
cm=trimesh.load('clamp_raw.stl');clamp=trimesh.Trimesh(C2S(cm.vertices),cm.faces)
def rotsteer(P,deg):
  L=S2L(P.reshape(-1,3));a=np.radians(deg);c,s=np.cos(a),np.sin(a)
  L=np.c_[c*L[:,0]-s*L[:,1],s*L[:,0]+c*L[:,1],L[:,2]];return L2S(L).reshape(P.shape)
# extra props: headlight lens, tablet, dash
a=np.radians(TAB_TILT);n=np.array([0,np.cos(a),np.sin(a)]);up=np.array([0,-np.sin(a),np.cos(a)])
def panel(c,n,up,w,h,th):
  b=trimesh.creation.box([w,h,th]);M=np.eye(4);M[:3,0]=[1,0,0];M[:3,1]=up;M[:3,2]=n;M[:3,3]=c;b.apply_transform(M);return b
tab=panel(TAB_C+n*2,n,up,145,80,8)
a2=np.radians(DASH_TILT);n2=np.array([0,np.cos(a2),np.sin(a2)]);up2=np.array([0,-np.sin(a2),np.cos(a2)])
dash=panel(DASH_C+n2*2,n2,up2,76,54,8)
lens=trimesh.creation.cylinder(radius=HL_R-3,segment=[HL_C+[0,9,0],HL_C+[0,11,0]])
def scene(lock):
  Tr=T.copy();Tr[rot]=rotsteer(T[rot],lock)
  items=[(Tr,np.where(rot[:,None],[[0.78,0.35,0.35]],[[0.74,0.74,0.76]])),(tw.triangles,np.tile([0.13,0.13,0.15],(len(tw.faces),1))),
         (clamp.triangles,np.tile([0.95,0.55,0.1],(len(clamp.faces),1))),(tab.triangles,np.tile([0.15,0.4,0.9],(12,1))),(dash.triangles,np.tile([0.1,0.75,0.45],(12,1))),
         (lens.triangles,np.tile([1,0.92,0.55],(len(lens.faces),1)))]
  return np.concatenate([i[0] for i in items]),np.concatenate([i[1] for i in items])
def view(ax,tris,cols,az,el,title,lims=None):
  a,e=np.radians(az),np.radians(el)
  fwd=np.array([np.cos(e)*np.sin(a),-np.cos(e)*np.cos(a),np.sin(e)])
  right=np.cross([0,0,1],fwd);right/=np.linalg.norm(right);up=np.cross(fwd,right)
  P2=np.stack([tris@right,tris@up],-1);depth=(tris@fwd).mean(1)
  nrm=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9
  Ld=fwd*0.6+up*0.6+right*0.3;Ld/=np.linalg.norm(Ld);sh=0.3+0.7*np.clip(nrm@Ld,0,1)**0.8
  spec=np.clip(nrm@Ld,0,1)**30*0.35
  o=np.argsort(depth);col=np.clip(cols[o]*sh[o,None]+spec[o,None],0,1)
  ax.add_collection(PolyCollection(P2[o],facecolors=col,edgecolors=col,linewidths=0.1))
  ax.autoscale();ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=14)
  if lims: ax.set_xlim(*lims[0]);ax.set_ylim(*lims[1])
t0_,c0=scene(0);t40,c40=scene(40)
fig,ax=plt.subplots(2,2,figsize=(18,18))
view(ax[0,0],t0_,c0,90,0,'Side, straight ahead')
view(ax[0,1],t0_,c0,-35,15,'3/4 front')
view(ax[1,0],t40,c40,160,28,"Rider's side, full lock 40°")
view(ax[1,1],t40,c40,-60,8,'3/4 front-left, full lock 40°')
plt.tight_layout();plt.savefig('tower-organic-v1-views.png',dpi=60)
cc=C2S(np.array([[0,60,-30]]))[0]
def crop(t,c,R=170):
  k=np.linalg.norm(t.mean(1)-cc,axis=1)<R;return t[k],c[k]
fig,ax=plt.subplots(1,2,figsize=(18,9))
view(ax[0],*crop(t40,c40),-70,12,'Mount close-up at full lock (40°): cheeks hug your clamp (orange)')
view(ax[1],*crop(t0_,c0),215,30,'Mount from behind-left: U-bolt side')
plt.tight_layout();plt.savefig('tower-organic-v1-mount.png',dpi=60)
