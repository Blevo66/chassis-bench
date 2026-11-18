import numpy as np,trimesh,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon,Circle
from scipy.spatial import ConvexHull
exec(open('tower.py').read().split("if __name__")[0])
T=np.load('T.npy');rot=np.load('rot.npy');sw=L2S(np.load('sw40.npy'))
cm=trimesh.load('clamp_raw.stl');CL=C2S(cm.vertices)
fig,(ax,ia)=plt.subplots(1,2,figsize=(17,13),gridspec_kw=dict(width_ratios=[3,1]))
# keep-out silhouettes (side projection) of steering sweep
for lim,col,lab in((95,'#f6d0d0','forks/bars swept at 40° lock, within ±95 mm of centre (keep the body out)'),(30,'#e79a9a','swept within ±30 mm (keep the neck out)')):
  P=sw[(abs(sw[:,0])<lim)&(sw[:,2]>40)&(sw[:,2]<480)&(sw[:,1]>-260)]
  H,xe,ye=np.histogram2d(P[:,1],P[:,2],bins=[np.arange(-260,140,3),np.arange(40,480,3)])
  ax.contourf((xe[:-1]+xe[1:])/2,(ye[:-1]+ye[1:])/2,(H.T>0).astype(float),levels=[0.5,1.5],colors=[col],zorder=1)
  ax.plot([],[],color=col,lw=10,label=lab)
# scan (side, painter)
L=np.array([0.3,-0.5,0.8]);L/=np.linalg.norm(L)
nrm=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9;sh=0.45+0.55*abs(nrm@L)
o=np.argsort(T[:,:,0].mean(1))
col=np.where(rot[o,None],[[0.85,0.55,0.55]],[[0.72,0.72,0.74]])*sh[o,None]
ax.add_collection(PolyCollection(T[o][:,:,[1,2]],facecolors=np.clip(col,0,1),edgecolors='none',zorder=2,alpha=0.55))
# clamp silhouette
h=ConvexHull(CL[:,[1,2]]);ax.add_patch(Polygon(CL[h.vertices][:,[1,2]],fc='#f39c12',ec='k',lw=1,zorder=3))
# ---------------- concept E (side view, scan Y fwd=left, Z up) ----------------
W='#f4f4f2';RED='#d0202a';BLU='#1d3f9a';K='#222'
def poly(pts,fc,z=5,ec=K,lw=1.4):ax.add_patch(Polygon(np.array(pts),closed=True,fc=fc,ec=ec,lw=lw,zorder=z))
# neck (from clamp front, through fork gap)
NK=C2S(np.array([[0,25,-38],[0,95,-38],[0,95,-150],[0,25,-150]]))[:,1:];poly(list(map(tuple,NK)),'#555',4)
# main side panel facets (white), beak, upper facet
poly([(-118,128),(-222,168),(-196,236),(-120,232)],W)            # lower facet / beak
poly([(-196,236),(-206,300),(-140,318),(-120,232)],W)             # lamp facet
poly([(-120,232),(-140,318),(-96,336),(-70,262)],'#e6e6e3')        # rear upper facet
poly([(-118,128),(-120,232),(-70,262),(-52,196)],'#e6e6e3')       # rear lower facet
# HRC stripes
poly([(-214,186),(-202,203),(-118,192),(-118,176)],RED,6,ec='none')
poly([(-208,212),(-200,224),(-119,212),(-119,200)],BLU,6,ec='none')
# twin lamps (side view: one lamp visible, front edge)
ax.add_patch(Polygon([(-204,236),(-214,300),(-196,302),(-188,240)],closed=True,fc='#333',ec=K,zorder=7))
ax.add_patch(Polygon([(-214,300),(-204,236),(-207,236),(-217,300)],closed=True,fc='#ffd75e',ec=K,zorder=8))
# screen (short, near vertical)
poly([(-206,300),(-196,312),(-150,440),(-160,442)],'#9fc3d8aa',6,ec='#345')
# tablet (5in) + dash (3in) stack, angled to rider
poly([(-150,410),(-58,372),(-54,382),(-146,420)],'#1a5fe0',7)      # tablet ~150 long (landscape width seen edge-on ~ its height 80) 
poly([(-150,410),(-140,318),(-96,336),(-58,372)],'#2b2b2b',5)      # nav back box
poly([(-112,352),(-76,340),(-72,350),(-108,362)],'#19b36b',8)      # 3in dash
ax.plot([],[],color='#1a5fe0',lw=6,label='5" tablet (top, angled at you)')
ax.plot([],[],color='#19b36b',lw=6,label='3" TFT dash (under the tablet)')
ax.plot([],[],color='#f39c12',lw=6,label='your headstock clamp (as placed)')
ax.plot([],[],color='#555',lw=6,label='neck through the fork gap (≤48 mm wide)')
ax.text(-232,268,'twin Baja\nlamps',ha='left',va='center',fontsize=11)
ax.text(-232,170,'beak',ha='left',fontsize=11)
ax.text(-158,452,'short upright screen',ha='center',fontsize=11)
ax.set_xlim(160,-330);ax.set_ylim(-40,490);ax.set_aspect('equal');ax.grid(alpha=.25)
ax.set_xlabel('mm (front of bike to the RIGHT)');ax.set_ylabel('mm');ax.legend(loc='lower right',fontsize=10)
ax.set_title('Option E concept, side view: narrow modern-Dakar tower, 80s details',fontsize=14)
# front view inset
def fpoly(pts,fc,ec=K):ia.add_patch(Polygon(np.array(pts),closed=True,fc=fc,ec=ec,lw=1.2))
fpoly([(-95,236),(-90,300),(-70,322),(70,322),(90,300),(95,236),(40,170),(-40,170)],W)
fpoly([(-70,322),(-58,442),(58,442),(70,322)],'#9fc3d8')
for x in(-46,46): ia.add_patch(Circle((x,270),42,fc='#ffd75e',ec=K,lw=1.2))
fpoly([(-75,395),(75,395),(75,412),(-75,412)],'#1a5fe0')
fpoly([(-24,170),(24,170),(24,110),(-24,110)],'#555')
for x in(-91,91): ia.plot([x,x],[60,240],color='#c55',lw=9,alpha=.6)
ia.text(0,62,'fork tubes 182 c-c',ha='center',fontsize=10)
ia.set_xlim(-140,140);ia.set_ylim(50,460);ia.set_aspect('equal');ia.axis('off');ia.set_title('Front view, same scale (~190 wide)',fontsize=13)
plt.savefig('optionE-side.png',dpi=90,bbox_inches='tight')
