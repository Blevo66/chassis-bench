import numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
exec(open('build_v1.py').read().split('parts={}')[0])
T=np.load('T.npy');rot=np.load('rot.npy')
def view(ax,az,el,box,title):
  c=T.mean(1);tri=T
  a,e=np.radians(az),np.radians(el)
  fwd=np.array([np.cos(e)*np.sin(a),-np.cos(e)*np.cos(a),np.sin(e)])
  right=np.cross([0,0,1],fwd) if abs(el)<89 else np.array([1.,0,0]);right/=np.linalg.norm(right);up=np.cross(fwd,right)
  P2=np.stack([tri@right,tri@up],-1);depth=(tri@fwd).mean(1)
  nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9
  L=fwd*0.7+up*0.5;L/=np.linalg.norm(L);sh=0.45+0.55*abs(nrm@L)
  col=np.where(rot[:,None],[[0.95,0.72,0.72]],[[0.78,0.78,0.8]])*sh[:,None]
  o=np.argsort(depth);ax.add_collection(PolyCollection(P2[o],facecolors=np.clip(col[o],0,1),edgecolors='none'))
  ax.set_xlim(*box[0]);ax.set_ylim(*box[1]);ax.set_aspect('equal')
  ax.set_xticks(np.arange(box[0][0]//50*50,box[0][1]+1,50));ax.set_yticks(np.arange(box[1][0]//50*50,box[1][1]+1,50))
  ax.grid(alpha=.35,lw=.6);ax.tick_params(labelsize=7);ax.set_title(title,fontsize=12)
fig=plt.figure(figsize=(12,12))
ax=fig.add_subplot(111)
# side view from the right, forward = left
view(ax,90,0,((-330,330),(-120,460)),'SIDE VIEW of the head (front of bike to the LEFT). Frame grey, forks/yokes/bars pink. Grid 50 mm.')
plt.tight_layout();plt.savefig('sketch-side.png',dpi=110)
fig=plt.figure(figsize=(12,12));ax=fig.add_subplot(111)
view(ax,180,89.9,((-330,330),(-260,400)),'TOP VIEW looking down (front of bike at the BOTTOM, rider at top). Grid 50 mm.')
plt.tight_layout();plt.savefig('sketch-top.png',dpi=110)
fig=plt.figure(figsize=(12,12));ax=fig.add_subplot(111)
view(ax,-40,20,((-330,330),(-160,470)),'3/4 FRONT-RIGHT view of the head. Grid 50 mm.')
ax.set_xlim(auto=True);ax.autoscale();plt.tight_layout();plt.savefig('sketch-34.png',dpi=110)
