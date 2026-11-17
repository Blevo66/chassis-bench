BUILD='build_v2.py'
import numpy as np,pickle,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
exec(open(BUILD).read().split('parts={}')[0])
parts=pickle.load(open('parts.pkl','rb'));T=np.load('T.npy');rot=np.load('rot.npy')
def rotsteer(P,deg):
  L=S2L(P.reshape(-1,3));a=np.radians(deg);c,s=np.cos(a),np.sin(a)
  L=np.c_[c*L[:,0]-s*L[:,1],s*L[:,0]+c*L[:,1],L[:,2]];return L2S(L).reshape(P.shape)
COL={'ubolt_top_55':(0.85,0.7,0.2),'top_plate':(0.6,0.62,0.66),'saddle':(0.6,0.62,0.66),'ubolt_lower':(0.85,0.7,0.2),'ubolt_upper':(0.85,0.7,0.2),'ubolt_lower_backbar':(0.6,0.62,0.66),'ubolt_upper_backbar':(0.6,0.62,0.66),'tower_shell':(0.15,0.15,0.17),'neck':(0.6,0.62,0.66),'bridge':(0.6,0.62,0.66),'plate_R':(0.6,0.62,0.66),'plate_L':(0.6,0.62,0.66),
 'bolt1':(0.85,0.7,0.2),'bolt2':(0.85,0.7,0.2),'headlight':(0.95,0.85,0.3),'tablet_5in':(0.1,0.35,0.85),'dash_3in_tft':(0.1,0.7,0.4)}
def scene(lock=0,alpha_shell=1):
  tris=[];cols=[]
  Tr=T.copy();Tr[rot]=rotsteer(T[rot],lock)
  tris.append(Tr);cols.append(np.where(rot[:,None],[[0.75,0.3,0.3]],[[0.72,0.72,0.72]]))
  for k,m in parts.items():
    tris.append(m.triangles);cols.append(np.tile(COL[k],(len(m.triangles),1)))
  return np.concatenate(tris),np.concatenate(cols)
def view(ax,tris,cols,az,el,title,lims=None):
  a,e=np.radians(az),np.radians(el)
  fwd=np.array([np.cos(e)*np.sin(a),-np.cos(e)*np.cos(a),np.sin(e)])  # camera->scene dir reversed
  right=np.cross([0,0,1],fwd);right/=np.linalg.norm(right);up=np.cross(fwd,right)
  P2=np.stack([tris@right,tris@up],-1);depth=(tris@fwd).mean(1)
  nrm=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9
  Ld=fwd*0.6+up*0.6+right*0.3;Ld/=np.linalg.norm(Ld);sh=0.35+0.65*abs(nrm@Ld)
  o=np.argsort(depth)
  ax.add_collection(PolyCollection(P2[o],facecolors=np.clip(cols[o]*sh[o,None],0,1),edgecolors='none'))
  ax.autoscale();ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=13)
  if lims: ax.set_xlim(*lims[0]);ax.set_ylim(*lims[1])
fig,ax=plt.subplots(2,2,figsize=(18,18))
t0,c0=scene(0);t45,c45=scene(45)
view(ax[0,0],t0,c0,90,0,'Side, straight ahead')
view(ax[0,1],t0,c0,-35,15,'3/4 front, straight ahead')
view(ax[1,0],t45,c45,140,30,"From behind and above, bars on full lock (45°, guessed)")
view(ax[1,1],t0,c0,90,0,'Close-up: top: your 55 ID U-bolt round the back of the head; bottom: U-bolt to the frame opening',lims=((-260,220),(-30,330)))
plt.tight_layout();plt.savefig('tower-v2-views.png',dpi=60)
