"""v4: rounded low-poly version of the twin pods. Smooth rounded sections at several stations,
sampled to a triangle mesh with every edge <= MAXE mm. Panels = ring strips between stations
(no interior vertices, so each unfolds flat exactly) + flat front/rear caps."""
import numpy as np, trimesh, shapely.geometry as sg, math
import tank
MAXE=150.0

def lerp(a,b,t): return {k:a[k]+(b[k]-a[k])*t for k in a}

def big(p):
    return max(p.geoms,key=lambda g:g.area) if p.geom_type=='MultiPolygon' else p
def fillet(pts,r_out,r_in,frac=0.45,nseg=12,keep=()):
    pts=np.asarray(pts,float); n=len(pts); out=[]
    ccw=sg.Polygon(pts).exterior.is_ccw
    for i in range(n):
        p0,p1,p2=pts[i-1],pts[i],pts[(i+1)%n]
        a=p0-p1; b=p2-p1; la,lb=np.linalg.norm(a),np.linalg.norm(b)
        if la<1e-6 or lb<1e-6: continue
        a/=la; b/=lb; th=np.arccos(np.clip(np.dot(a,b),-1,1))
        if th>np.radians(178) or i in keep: out.append(p1); continue
        cross=(p1-p0)[0]*(p2-p1)[1]-(p1-p0)[1]*(p2-p1)[0]
        convex=(cross>0)==ccw
        r=r_out if convex else r_in
        d=min(r/np.tan(th/2),frac*la,frac*lb); r=d*np.tan(th/2)
        t1=p1+a*d; t2=p1+b*d; bis=(a+b)/np.linalg.norm(a+b); c=p1+bis*(r/np.sin(th/2))
        a1=np.arctan2(*(t1-c)[::-1]); a2=np.arctan2(*(t2-c)[::-1])
        da=(a2-a1+np.pi)%(2*np.pi)-np.pi
        for u in np.linspace(0,1,nseg): out.append(c+r*np.array([np.cos(a1+da*u),np.sin(a1+da*u)]))
    return sg.Polygon(out)

def ring_poly(P,t,r1=45.,r2=30.):
    s=lerp(P['rear'],P['front'],t)
    k=0.5+0.5*t                      # smaller radii at the small rear end
    return fillet(tank.section(s,P),r1*k,r2*k)

LAM=90.0   # mm of 'weight' per radian of turning: puts more points round the corners
def sample(poly,N,start,phase=0.0):
    ring=sg.LineString(poly.exterior.coords)
    if not sg.Polygon(ring).exterior.is_ccw: ring=sg.LineString(list(ring.coords)[::-1])
    d0=ring.project(sg.Point(start)); L=ring.length
    M=3000; d=(d0+L*np.arange(M)/M)%L
    Q=np.array([ring.interpolate(x).coords[0] for x in d])
    seg=np.diff(np.vstack([Q,Q[:1]]),axis=0); ang=np.arctan2(seg[:,1],seg[:,0])
    turn=np.abs((np.diff(np.concatenate([ang,ang[:1]]))+np.pi)%(2*np.pi)-np.pi)
    w=np.concatenate([[0],np.cumsum(np.linalg.norm(seg,axis=1)+LAM*turn)])
    tgt=((np.arange(N)+phase)%N)*w[-1]/N
    idx=np.searchsorted(w,tgt); idx=np.clip(idx,0,M-1)
    return Q[idx]

STAGGER=False
def build(P,side=+1,nst=None,N=None):
    xr,xf=P['x_rear'],P['x_front']
    if nst is None: nst=int(math.ceil((xf-xr)/105.))+1
    ts=np.linspace(0,1,nst)
    polys=[ring_poly(P,t) for t in ts]
    if N is None: N=int(math.ceil(max(p.exterior.length for p in polys)/100.))
    rings=[]
    for t,p in zip(ts,polys):
        s=lerp(P['rear'],P['front'],t)
        ai=len(rings)
        Y=sample(p,N,(P['inner_gap'],s['zt']),0.5*(ai%2) if STAGGER else 0.0)
        x=xr+(xf-xr)*t
        rings.append(np.column_stack([np.full(N,x),P['spine_y']+side*Y[:,0],Y[:,1]]))
    return rings,ts

def mesh_from(rings,shorter=True):
    nst=len(rings); N=len(rings[0]); V=np.vstack(rings); faces=[]; bands=[]
    for a in range(nst-1):
        band=[]
        for k in range(N):
            k2=(k+1)%N; i0,i1,j0,j1=a*N+k,a*N+k2,(a+1)*N+k,(a+1)*N+k2
            if STAGGER:
                # ring a+1 is offset half a step: B_k sits between A_k and A_k+1 (a even) or the other way round
                tri=[(i0,j0,i1),(i1,j0,j1)] if a%2==0 else [(i0,j0,j1),(i0,j1,i1)]
            elif np.linalg.norm(V[i0]-V[j1])<=np.linalg.norm(V[i1]-V[j0]):
                tri=[(i0,j0,j1),(i0,j1,i1)]
            if STAGGER: pass
            elif False:
                tri=[(i0,j0,i1),(i1,j0,j1)]
            band+=tri
        faces+=band; bands.append(band)
    caps=[]
    for a,off in ((0,0),(nst-1,(nst-1)*N)):
        R=rings[a]; poly=sg.Polygon(R[:,1:])
        v2,f2=trimesh.creation.triangulate_polygon(poly,engine='earcut')
        idx=[int(np.argmin(np.linalg.norm(R[:,1:]-v,axis=1))) for v in v2]
        cap=[(off+idx[f[0]],off+idx[f[1]],off+idx[f[2]]) for f in f2]; faces+=cap; caps.append(cap)
    m=trimesh.Trimesh(V,faces,process=False)
    trimesh.repair.fix_normals(m)
    return m,V,bands,caps

def edges_max(V,bands):
    e=0
    for band in bands:
        for f in band:
            for i in range(3): e=max(e,np.linalg.norm(V[f[i]]-V[f[(i+1)%3]]))
    return e

def unfold_band(V,band,cut_after=None):
    """band: triangles in strip order (consecutive share an edge). Returns list of 2D tris (same order), fold lines."""
    P2={}; f0=band[0]
    a,b,c=V[f0[0]],V[f0[1]],V[f0[2]]
    ab=np.linalg.norm(b-a); P2[f0[0]]=np.array([0.,0.]); P2[f0[1]]=np.array([ab,0.])
    def put(i,j,k,other):
        A,B,C=V[i],V[j],V[k]; e=B-A; L=np.linalg.norm(e); u=e/L
        t=np.dot(C-A,u); h=np.linalg.norm((C-A)-t*u)
        a2,b2=P2[i],P2[j]; e2=(b2-a2)/np.linalg.norm(b2-a2); n2=np.array([-e2[1],e2[0]])
        p=a2+t*e2+h*n2
        if other is not None and np.dot(P2[other]-a2,n2)>0: p=a2+t*e2-h*n2
        return p
    P2[f0[2]]=put(f0[0],f0[1],f0[2],None)
    tris2=[[P2[f0[0]],P2[f0[1]],P2[f0[2]]]]; folds=[]; prev=f0
    for f in band[1:]:
        sh=[v for v in f if v in prev]; new=[v for v in f if v not in prev][0]; oth=[v for v in prev if v not in sh][0]
        # positions for this face use a local dict so ring closure (vertex reused at the end) does not clash
        p=put(sh[0],sh[1],new,oth)
        folds.append((P2[sh[0]].copy(),P2[sh[1]].copy(),fold_angle(V,prev,f,sh)))
        P2_new=p
        P2[new]=P2_new
        tris2.append([P2[v] for v in f]); prev=f
    return tris2,folds

def fold_angle(V,f1,f2,sh):
    n1=np.cross(V[f1[1]]-V[f1[0]],V[f1[2]]-V[f1[0]]); n2=np.cross(V[f2[1]]-V[f2[0]],V[f2[2]]-V[f2[0]])
    return float(np.degrees(np.arccos(np.clip(np.dot(n1,n2)/np.linalg.norm(n1)/np.linalg.norm(n2),-1,1))))
