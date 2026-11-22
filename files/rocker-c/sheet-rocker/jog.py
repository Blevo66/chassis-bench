import os
import pickle, numpy as np, trimesh, manifold3d as m3, sys, json
from shapely.geometry import Point, Polygon, LineString, box
from shapely import affinity
T=float(sys.argv[1]) if len(sys.argv)>1 else 5.0
OFF=17.25
O=pickle.load(open('outlines.pkl','rb'))
P=np.array([0,0.]); S=np.array([-166.8,64.4]); D=np.array([-100.5,-100.3])
u=np.array([-1,-1])/np.sqrt(2)              # arm axis, towards D
Q1=np.array([-45.,-35.]); RUN=float(sys.argv[2]) if len(sys.argv)>2 else 22.8
s1=0.0; s2=RUN
sd=lambda p: (np.asarray(p)-Q1)@u
wv=np.array([-1,1])/np.sqrt(2); TMAX=70.0  # only the lower arm side of the bend line jogs
def zj(p): p=np.asarray(p); return zoff(sd(p)) if (p-Q1)@wv<TMAX else 0.0
outline=O['o2'].buffer(0)                    # full side silhouette, windows filled
HOLE=10.5/2
def zoff(s): t=np.clip((s-s1)/(s2-s1),0,1); return OFF*(3*t*t-2*t**3)
def plate(z0):
    # triangulate the outline (minus holes) finely, extrude, then displace z by zoff(s)
    poly=outline
    for c in (P,S,D): poly=poly.difference(Point(*c).buffer(HOLE,32))
    import os; poly=poly.segmentize(float(os.environ.get('SEG','2')))
    v,f=trimesh.creation.triangulate_polygon(poly,engine='triangle',triangle_args='pq30a'+os.environ.get('AREA','6'))
    m=trimesh.creation.extrude_triangulation(v,f,T)
    vv=m.vertices.copy(); vv[:,2]+=z0+np.array([zj(p[:2]) for p in vv])
    return trimesh.Trimesh(vv,m.faces,process=True)
def man(t): return m3.Manifold(m3.Mesh(np.asarray(t.vertices,np.float32),np.asarray(t.faces,np.uint32)))
def tri(mf): mm=mf.to_mesh(); return trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts))
zL=-14.6; zR=14.6-T
L=plate(zL); R=plate(zR)
gap0=zR-(zL+T)
def tube(c,z0,z1,od=20,idd=10.5):
    o=trimesh.creation.cylinder(od/2,z1-z0,sections=48); o.apply_translation((c[0],c[1],(z0+z1)/2))
    i=trimesh.creation.cylinder(idd/2,z1-z0+4,sections=32); i.apply_translation((c[0],c[1],(z0+z1)/2))
    return man(o)-man(i)
def web(c,ang,length,z0,z1,w=T):
    b=trimesh.creation.box((length,w,z1-z0)); b.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ang),(0,0,1))); b.apply_translation((c[0],c[1],(z0+z1)/2)); return man(b)
# webs: flat bar between plates, set 4 mm inside the edge, following the local edge direction
def edgeweb(pt,length=40):
    ext=outline.exterior; d=ext.project(Point(*pt)); a=np.array(ext.interpolate(d-3).coords[0]); b=np.array(ext.interpolate(d+3).coords[0])
    tng=(b-a)/np.linalg.norm(b-a); nrm=np.array([-tng[1],tng[0]])
    c=np.array(ext.interpolate(d).coords[0]); cin=c+nrm*(T/2+4)
    if not outline.contains(Point(*cin)): cin=c-nrm*(T/2+4)
    return cin,np.degrees(np.arctan2(tng[1],tng[0])),length
WEBS=[edgeweb((-70,84),50),edgeweb((-125,44),40),edgeweb((-5,-30),30)]
# web 4: floor of the dogbone slot, right after the jog, across the arm (stops the jog unbending)
c4=Q1+u*(RUN+T/2+0.7); _o=(c4-Q1)@wv; WEBS.append((np.array([-60.9,-56.5]) if False else Q1+u*(RUN+T/2+0.7)+wv*(-1.0),135.0,54))
asm=man(L)+man(R)+tube(P,zL+T,zR)+tube(S,zL+T,zR)
for c,a,lgt in WEBS:
    o=zj(c); asm=asm+web(c,a,lgt,zL+T+o,zR+o)
out=tri(asm); out.export(f'jog_{int(T)}'+os.environ.get('SUF','')+'.stl')
print('T',T,'upper gap',round(gap0,2),'lower cheeks z',(round(zL+OFF,2),round(zL+OFF+T,2)),(round(zR+OFF,2),round(zR+OFF+T,2)),'slot',round(zR+OFF-(zL+OFF+T),2))
print('watertight',out.is_watertight,'vol cm3',round(out.volume/1000,1),'kg steel',round(out.volume/1000*7.85/1000,2))
json.dump(dict(T=T,zL=zL,zR=zR,OFF=OFF,Q1=Q1.tolist(),u=u.tolist(),RUN=RUN,webs=[(list(map(float,c)),float(a),l) for c,a,l in WEBS]),open(f'jog_{int(T)}'+os.environ.get('SUF','')+'.json','w'))
