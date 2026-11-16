import sys, numpy as np, trimesh, ezdxf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tank
OUT=sys.argv[1]
frame=trimesh.load('/mnt/project-files/frame-scan/fusion/xl125r-frame-scan-full.stl')
L=tank.half_mesh(tank.P,1); R=tank.half_mesh(tank.P,-1)
fv=frame.vertices
def outline(ax,m,i,j,**kw):
    from shapely.geometry import MultiPoint
    h=MultiPoint(m.vertices[:,[i,j]]).convex_hull
    x,y=h.exterior.xy; ax.fill(x,y,alpha=.45,**kw); ax.plot(x,y,'k',lw=1)
fig,ax=plt.subplots(1,3,figsize=(20,7),gridspec_kw={'width_ratios':[2.2,1,1]})
ax[0].scatter(fv[:,0],fv[:,2],s=.05,c='0.4'); outline(ax[0],L,0,2,color='#b0b8c0')
for k in range(7):
    p=L.vertices; 
F=tank.section(tank.P['front'],tank.P); Rr=tank.section(tank.P['rear'],tank.P)
for (y1,z1),(y2,z2) in zip(F,Rr): ax[0].plot([tank.P['x_front'],tank.P['x_rear']],[z1,z2],'k',lw=.6)
ax[0].set_title('Side view (left), frame scan. X fwd from swingarm pivot, mm'); ax[0].set_aspect('equal'); ax[0].grid(alpha=.3); ax[0].set_xlim(-420,560); ax[0].set_ylim(-120,620)
s=fv[:,0]>-50
ax[1].scatter(fv[s,1],fv[s,0],s=.05,c='0.4'); outline(ax[1],L,1,0,color='#b0b8c0'); outline(ax[1],R,1,0,color='#b0b8c0')
ax[1].set_title('Top view (Y left is right of plot? no: Y left = +)'); ax[1].set_aspect('equal'); ax[1].grid(alpha=.3); ax[1].invert_xaxis(); ax[1].set_title('Top view, front at top')
for x,key,c in ((tank.P['x_front'],'front','C0'),(tank.P['x_rear'],'rear','C1')):
    S=tank.section(tank.P[key],tank.P); S=np.vstack([S,S[:1]])
    for sd in (1,-1): ax[2].plot(tank.P['spine_y']+sd*S[:,0],S[:,1],c,label=f'{key} end' if sd==1 else None)
    sec=frame.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
    if sec is not None: ax[2].scatter(sec.vertices[:,1],sec.vertices[:,2],s=1,c=c)
ax[2].legend(); ax[2].set_aspect('equal'); ax[2].grid(alpha=.3); ax[2].set_title('Ends looking forward, with frame section')
plt.tight_layout(); plt.savefig(f'{OUT}/tank-on-frame-views.png',dpi=80)
# 3D render
fig=plt.figure(figsize=(12,9)); a=fig.add_subplot(111,projection='3d')
for m in (L,R):
    a.add_collection3d(Poly3DCollection(m.triangles,facecolor='#c8ced4',edgecolor='#555',lw=.3,alpha=.95))
a.scatter(fv[::3,0],fv[::3,1],fv[::3,2],s=.1,c='0.3')
a.set_xlim(-150,500);a.set_ylim(-325,325);a.set_zlim(150,650); a.view_init(25,-60); a.set_box_aspect((650,650,500)); a.set_axis_off()
plt.tight_layout(); plt.savefig(f'{OUT}/tank-3d.png',dpi=80)
# flats
import glob
fl=sorted(glob.glob(f'{OUT}/flat-*.dxf')); fig,ax=plt.subplots(1,len(fl),figsize=(5*len(fl),6))
for a,f in zip(ax,fl):
    d=ezdxf.readfile(f)
    for e in d.modelspace():
        if e.dxftype()=='LWPOLYLINE': p=np.array([q[:2] for q in e.get_points()]); p=np.vstack([p,p[:1]]); a.plot(p[:,0],p[:,1],'r')
        elif e.dxftype()=='LINE': a.plot([e.dxf.start[0],e.dxf.end[0]],[e.dxf.start[1],e.dxf.end[1]],'b--')
        elif e.dxftype()=='CIRCLE':
            t=np.linspace(0,2*np.pi,50); a.plot(e.dxf.center[0]+e.dxf.radius*np.cos(t),e.dxf.center[1]+e.dxf.radius*np.sin(t),'r')
        elif e.dxftype()=='TEXT' and 'BEND' in e.dxf.text: a.text(e.dxf.insert[0],e.dxf.insert[1],e.dxf.text,fontsize=8,color='b')
    a.set_aspect('equal'); a.grid(alpha=.3); a.set_title(f.split('/')[-1])
plt.tight_layout(); plt.savefig(f'{OUT}/flat-patterns.png',dpi=70)
