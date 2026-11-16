import sys, pickle, numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource
OUT=sys.argv[1]
frame=trimesh.load('/mnt/project-files/frame-scan/fusion/xl125r-frame-scan-full.stl'); fv=frame.vertices
L=trimesh.load(f'{OUT}/tank-left-half.stl'); R=trimesh.load(f'{OUT}/tank-right-half.stl')
def shade(m,view):
    n=m.face_normals; l=np.array(view)/np.linalg.norm(view); k=np.clip(n@l,0,1)
    return [(0.55+0.4*v,0.58+0.4*v,0.62+0.37*v) for v in k]
fig=plt.figure(figsize=(18,9))
for i,(el,az) in enumerate(((18,-35),(15,-120))):
    a=fig.add_subplot(1,2,i+1,projection='3d')
    for m in (L,R):
        a.add_collection3d(Poly3DCollection(m.triangles,facecolors=shade(m,[np.cos(np.radians(az)),np.sin(np.radians(az)),1.2]),edgecolor='none'))
        fe=m.face_adjacency_edges[np.degrees(m.face_adjacency_angles)>3]
        from mpl_toolkits.mplot3d.art3d import Line3DCollection
        a.add_collection3d(Line3DCollection(m.vertices[fe],colors='#222',lw=.7))
    a.scatter(fv[::2,0],fv[::2,1],fv[::2,2],s=.15,c='0.35')
    a.set_xlim(-150,500);a.set_ylim(-325,325);a.set_zlim(50,600); a.set_box_aspect((650,650,550)); a.view_init(el,az); a.set_axis_off()
plt.tight_layout(); plt.savefig(f'{OUT}/tank-3d.png',dpi=75)
# orthographic views
fig,ax=plt.subplots(1,3,figsize=(20,7),gridspec_kw={'width_ratios':[2.2,1,1]})
ax[0].scatter(fv[:,0],fv[:,2],s=.05,c='0.4')
for e in L.face_adjacency_edges[np.degrees(L.face_adjacency_angles)>3]: p=L.vertices[e]; ax[0].plot(p[:,0],p[:,2],'k',lw=.5)
ax[0].set_aspect('equal'); ax[0].grid(alpha=.3); ax[0].set_title('Side view (left half), frame scan. mm from swingarm pivot'); ax[0].set_xlim(-420,560); ax[0].set_ylim(-120,620)
s=fv[:,0]>-50; ax[1].scatter(fv[s,1],fv[s,0],s=.05,c='0.4')
for m in (L,R):
    for e in m.face_adjacency_edges[np.degrees(m.face_adjacency_angles)>3]: p=m.vertices[e]; ax[1].plot(p[:,1],p[:,0],'k',lw=.4)
ax[1].invert_xaxis(); ax[1].set_aspect('equal'); ax[1].grid(alpha=.3); ax[1].set_title('Top view, front at top')
s=fv[:,0]>250; ax[2].scatter(fv[s,1],fv[s,2],s=.05,c='0.6')
for m in (L,R):
    for e in m.face_adjacency_edges[np.degrees(m.face_adjacency_angles)>3]: p=m.vertices[e]; ax[2].plot(p[:,1],p[:,2],'k',lw=.4)
ax[2].set_aspect('equal'); ax[2].grid(alpha=.3); ax[2].set_title('Front view')
plt.tight_layout(); plt.savefig(f'{OUT}/tank-on-frame-views.png',dpi=75)
# flats
flats=pickle.load(open(f'{OUT}/.flats.pkl','rb'))
names=['rear-face','strip-1','strip-2','strip-3','front-cone-top','front-cone-bottom']
fig=plt.figure(figsize=(22,12)); gs=fig.add_gridspec(2,4)
pos={'rear-face':gs[1,0],'strip-1':gs[0,0],'strip-2':gs[0,1:3],'strip-3':gs[0,3],'front-cone-top':gs[1,1],'front-cone-bottom':gs[1,2]}
for n in names:
    if pos[n] is None: continue
    a=fig.add_subplot(pos[n]); f=flats[n]; poly=f[0]; x,y=poly.exterior.xy; a.plot(x,y,'r',lw=1.2)
    for fl in f[1]:
        if fl[2]<3: continue
        a.plot([fl[0][0],fl[1][0]],[fl[0][1],fl[1][1]],'b--' if fl[3]=='out' else 'g--',lw=.7)
    if len(f)>3:
        t=np.linspace(0,2*np.pi,60); a.plot(f[3][0]+50*np.cos(t),f[3][1]+50*np.sin(t),'m',lw=1.5); a.text(f[3][0],f[3][1],'filler pad',color='m',ha='center')
    if len(f)>2:
        for (c,r) in f[2]: t=np.linspace(0,2*np.pi,40); a.plot(c[0]+r*np.cos(t),c[1]+r*np.sin(t),'r',lw=1)
    a.set_aspect('equal'); a.grid(alpha=.3); a.set_title(f'{n}  (blue = fold out, green = fold IN)' if f[1] else n)
plt.tight_layout(); plt.savefig(f'{OUT}/flat-patterns.png',dpi=65)
