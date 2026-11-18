import numpy as np,trimesh,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon,Circle,Ellipse
from scipy.spatial import ConvexHull
exec(open('tower.py').read().split("if __name__")[0])
T=np.load('T.npy');rot=np.load('rot.npy');sw=L2S(np.load('sw40.npy'))
cm=trimesh.load('clamp_raw.stl');CL=C2S(cm.vertices);hcl=ConvexHull(CL[:,[1,2]])
P=sw[(abs(sw[:,0])<95)&(sw[:,2]>40)&(sw[:,2]<480)&(sw[:,1]>-260)]
H,xe,ye=np.histogram2d(P[:,1],P[:,2],bins=[np.arange(-260,140,3),np.arange(40,480,3)])
L=np.array([0.3,-0.5,0.8]);L/=np.linalg.norm(L)
nrm=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9;sh=0.45+0.55*abs(nrm@L)
o=np.argsort(T[:,:,0].mean(1));col=np.clip(np.where(rot[o,None],[[0.85,0.55,0.55]],[[0.72,0.72,0.74]])*sh[o,None],0,1)
W='#f4f4f2';G='#e2e2df';RED='#d0202a';BLU='#1d3f9a';K='#222';SCR='#9fc3d8';NAV='#2b2b2b';TAB='#1a5fe0';DSH='#19b36b';LMP='#ffd75e'
def base(ax,title):
  ax.contourf((xe[:-1]+xe[1:])/2,(ye[:-1]+ye[1:])/2,(H.T>0).astype(float),levels=[0.5,1.5],colors=['#f6d0d0'],zorder=1)
  ax.add_collection(PolyCollection(T[o][:,:,[1,2]],facecolors=col,edgecolors='none',zorder=2,alpha=0.45))
  ax.add_patch(Polygon(CL[hcl.vertices][:,[1,2]],fc='#f39c12',ec='k',lw=.8,zorder=3))
  ax.set_xlim(150,-230);ax.set_ylim(20,470);ax.set_aspect('equal');ax.axis('off');ax.set_title(title,fontsize=13)
def p(ax,pts,fc,z=5,ec=K,lw=1.3):ax.add_patch(Polygon(np.array(pts),closed=True,fc=fc,ec=ec,lw=lw,zorder=z))
def lamp_side(ax,x,y,h=64,d=50):p(ax,[(x,y-h/2),(x,y+h/2),(x+d,y+h/2-6),(x+d,y-h/2+6)],'#333',7);p(ax,[(x,y-h/2),(x,y+h/2),(x-3,y+h/2),(x-3,y-h/2)],LMP,8)
def stack(ax,x0,y0):  # tablet+dash stack, x0 front top
  p(ax,[(x0,y0),(x0+95,y0-36),(x0+99,y0-26),(x0+4,y0+10)],TAB,7);p(ax,[(x0+30,y0-55),(x0+66,y0-67),(x0+70,y0-57),(x0+34,y0-45)],DSH,8)
NK=[tuple(q) for q in C2S(np.array([[0,25,-38],[0,95,-38],[0,95,-95],[0,25,-95]]))[:,1:]]
fig,axs=plt.subplots(2,3,figsize=(21,15))
# 1 Lamp plate (minimal Baja): flat plate with twin lamps, small screen, no nose
ax=axs[0,0];base(ax,'1. Baja lamp plate: no nose, flat plate')
p(ax,NK,'#555',4);p(ax,[(-48,120),(-80,320),(-66,322),(-34,125)],'#555',4)
p(ax,[(-92,215),(-104,300),(-84,304),(-72,220)],W);lamp_side(ax,-104,262)
p(ax,[(-104,302),(-92,306),(-70,420),(-80,422)],SCR,6,'#345');p(ax,[(-80,330),(-8,345),(-8,365),(-75,392)],NAV,5);stack(ax,-75,392)
# 2 Shield (modern KTM-ish): tall slim, near-vertical front, lamps stacked low in it
ax=axs[0,1];base(ax,'2. Tall slim shield (modern works bike)')
p(ax,NK,'#555',4);p(ax,[(-60,135),(-112,165),(-118,300),(-104,440),(-90,442),(-40,330),(-22,250),(-40,165)],W)
p(ax,[(-112,170),(-116,220),(-60,214),(-58,190)],RED,6,'none');lamp_side(ax,-118,250,56,44)
p(ax,[(-104,440),(-92,446),(-86,470),(-96,468)],SCR,6,'#345');p(ax,[(-90,442),(-40,330),(0,350),(5,395)],NAV,5);stack(ax,-88,410)
# 3 Wedge beak (CRF450 Rally-ish): pointed beak, rising to screen
ax=axs[0,2];base(ax,'3. Wedge beak (modern Honda rally)')
p(ax,NK,'#555',4);p(ax,[(-60,135),(-158,168),(-130,250),(-108,330),(-40,330),(-20,250),(-42,165)],W)
p(ax,[(-150,174),(-138,202),(-62,190),(-60,170)],RED,6,'none');p(ax,[(-134,212),(-128,226),(-64,214),(-63,202)],BLU,6,'none')
lamp_side(ax,-132,268,56,44);p(ax,[(-108,330),(-98,334),(-74,440),(-84,442)],SCR,6,'#345');p(ax,[(-84,420),(-108,330),(-40,330),(4,380)],NAV,5);stack(ax,-84,412)
# 4 80s number-board: rounded oval board with lamps, short screen
ax=axs[1,0];base(ax,'4. 80s rounded number board')
p(ax,NK,'#555',4);p(ax,[(-40,130),(-70,200),(-58,206),(-30,138)],'#555',4);ax.add_patch(Ellipse((-78,250),70,190,angle=-12,fc='#ffd400',ec=K,lw=1.3,zorder=5))
lamp_side(ax,-104,262,70,46);p(ax,[(-98,345),(-86,348),(-72,430),(-82,432)],SCR,6,'#345');p(ax,[(-60,340),(0,350),(4,380),(-74,395)],NAV,5);stack(ax,-74,395)
# 5 Low fairing that flows into the tanks
ax=axs[1,1];base(ax,'5. Rounded 80s works fairing (tank panels separate)')
p(ax,NK,'#555',4);p(ax,[(-60,135),(-135,170),(-120,300),(-60,320),(-20,300),(-18,240),(-40,165)],W)
p(ax,[(-130,180),(-126,200),(-30,215),(-34,198)],RED,6,'none');p(ax,[(-124,210),(-122,222),(-22,240),(-22,226)],BLU,6,'none')
lamp_side(ax,-128,262,60,44);p(ax,[(-120,300),(-110,304),(-86,410),(-96,412)],SCR,6,'#345');p(ax,[(-96,400),(-110,305),(-40,320),(0,370)],NAV,5);stack(ax,-94,402)
# 6 Faceted folded-sheet (like your tank): few big flat facets, square-ish
ax=axs[1,2];base(ax,'6. Folded-sheet facets (matches your tank)')
p(ax,NK,'#555',4);p(ax,[(-60,135),(-128,175),(-118,240),(-58,226)],W);p(ax,[(-118,240),(-124,310),(-60,322),(-58,226)],G)
p(ax,[(-58,226),(-60,322),(-24,300),(-22,240),(-40,165),(-60,135)],'#d5d5d1')
lamp_side(ax,-124,270,58,44);p(ax,[(-124,312),(-112,318),(-88,425),(-98,427)],SCR,6,'#345');p(ax,[(-98,410),(-112,318),(-40,322),(0,370)],NAV,5);stack(ax,-96,408)
fig.suptitle('Tower shape options, side view to scale (front of bike to the RIGHT). Pink = forks/bars at full lock. Orange = your clamp.',fontsize=15)
plt.tight_layout(rect=[0,0,1,0.97]);plt.savefig('tower-shapes-sheet.png',dpi=70)
