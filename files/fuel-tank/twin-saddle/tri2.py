"""v5: big crisp triangles (sides close to, never over, MAXE), staggered rings, ends tapered to a point
(no flat end plates). Every panel is a strip with all its vertices on the edge, so it unfolds flat exactly."""
import numpy as np, trimesh, shapely.geometry as sg, math
import tank, tri
MAXE=150.0

def section_poly(P,t,scale=1.0,r1=30.,r2=20.):
    s=tri.lerp(P['rear'],P['front'],t)
    p=tri.fillet(tank.section(s,P),r1,r2)
    if scale!=1.0:
        c=np.array(p.centroid.coords[0]); q=(np.array(p.exterior.coords)-c)*scale+c; p=sg.Polygon(q)
    return p

def stations(P,tip=60.,tip_scale=0.5):
    xr,xf=P['x_rear'],P['x_front']; L=xf-xr
    xs=[xr, xr+tip]+list(np.linspace(xr+tip,xf-tip,3)[1:-1])+[xf-tip, xf]
    return [(x,(x-xr)/L,(tip_scale if i in (0,len(xs)-1) else 1.0)) for i,x in enumerate(xs)]

def build(P,side=+1,N=10,st=None,apex_out=20.,LAM=30.):
    st=st or stations(P); rings=[]
    tri.LAM=LAM
    for i,(x,t,sc) in enumerate(st):
        p=section_poly(P,t,sc); s=tri.lerp(P['rear'],P['front'],t)
        Y=tri.sample(p,N,(P['inner_gap'],s['zt']),0.5*(i%2))
        rings.append(np.column_stack([np.full(N,x),P['spine_y']+side*Y[:,0],Y[:,1]]))
    # apexes: centroid of the tip ring, pushed out a little
    ap=[]
    for r,d in ((rings[0],-apex_out),(rings[-1],apex_out)):
        c=r.mean(0); c[0]+=d; ap.append(c)
    return rings,ap

def mesh(rings,ap):
    nst=len(rings); N=len(rings[0]); V=np.vstack(rings+[ap[0][None],ap[1][None]]); A0=nst*N; A1=A0+1
    bands=[]
    for a in range(nst-1):
        band=[]
        for k in range(N):
            k2=(k+1)%N; i0,i1,j0,j1=a*N+k,a*N+k2,(a+1)*N+k,(a+1)*N+k2
            # ring a+1 is half a step ahead of ring a when a is even, half a step behind when odd
            band+= [(i0,j0,i1),(i1,j0,j1)] if a%2==0 else [(i0,j0,j1),(i0,j1,i1)]
        bands.append(band)
    rear=[(A0,k,(k+1)%N) for k in range(N)]
    front=[(A1,(nst-1)*N+k,(nst-1)*N+(k+1)%N) for k in range(N)]
    panels=[('rear-cone',rear)]+[(f'strip-{i+1}',b) for i,b in enumerate(bands)]+[('front-cone',front)]
    faces=[f for _,b in panels for f in b]
    m=trimesh.Trimesh(V,faces,process=False); trimesh.repair.fix_normals(m)
    return m,V,panels

def max_edge(V,panels):
    e=0
    for _,b in panels:
        for f in b:
            for i in range(3): e=max(e,np.linalg.norm(V[f[i]]-V[f[(i+1)%3]]))
    return e
