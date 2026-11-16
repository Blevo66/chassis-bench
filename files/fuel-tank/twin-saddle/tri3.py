"""v6: big crisp triangles, a flat top deck on each half (filler pad), flat 80 mm vertical rear face for the seat,
full rounded front tapering to a short point. Panels are loft strips between stations (all vertices on the edge)."""
import numpy as np, trimesh, shapely.geometry as sg, shapely.ops as so, math
import tank, tri

def section(P,t,r1=30.,r2=20.):
    s=tri.lerp(P['rear'],P['front'],t)
    S=tank.section(s,P)                     # A=0 inner top, B=1 top outer
    poly=tri.fillet(S,r1,r2,keep=(0,1))     # keep the top deck corners sharp
    return poly,S[0],S[1]

def ring(P,x,t,N,phase,scale=1.0):
    poly,A,B=section(P,t)
    C=np.array(poly.centroid.coords[0])
    def sc(p): return (np.asarray(p)-C)*scale+C
    ringl=sg.LineString(list(poly.exterior.coords))
    if not poly.exterior.is_ccw: ringl=sg.LineString(list(ringl.coords)[::-1])
    L=ringl.length; dA=ringl.project(sg.Point(A)); dB=ringl.project(sg.Point(B)); dT=ringl.project(sg.Point((A+B)/2))
    # walk from B to A the long way (not across the top deck)
    fwd=(dA-dB)%L; dTf=(dT-dB)%L
    if dTf<fwd:   # forward passes the deck: go backwards
        span=-((dB-dA)%L)
    else:
        span=fwd
    M=N-2
    ds=[(dB+span*(i+phase)/(M+1))%L for i in range(1,M+1)]
    pts=[A,B]+[ringl.interpolate(d).coords[0] for d in ds]
    return np.array([sc(p) for p in pts]),poly

def loft(Ra,Rb,ia,ib):
    """greedy loft between closed rings Ra (indices ia) and Rb (indices ib), both starting at the aligned point 0.
    Returns triangles in strip order."""
    na,nb=len(ia),len(ib); i=j=0; tris=[]
    while i<na or j<nb:
        a0,b0=ia[i%na],ib[j%nb]
        if i==na: tris.append((a0,b0,ib[(j+1)%nb])); j+=1; continue
        if j==nb: tris.append((a0,b0,ia[(i+1)%na])); i+=1; continue
        a1,b1=ia[(i+1)%na],ib[(j+1)%nb]
        if np.linalg.norm(Ra[a0]-Rb[b1])<=np.linalg.norm(Rb[b0]-Ra[a1]): tris.append((a0,b0,b1)); j+=1
        else: tris.append((a0,b0,a1)); i+=1
    return tris

def build(P,side=1,N=9,xs=(20,80,140,260,345),rear_h=80.,front_tip=(0.8,15.)):
    xr,xf=P['x_rear'],P['x_front']; rings=[]
    for k,x in enumerate(xs):
        t=(x-xr)/(xf-xr); sc=1.0
        if k==0:
            p,_,_=section(P,t); zz=np.array(p.exterior.coords)[:,1]; sc=rear_h/np.ptp(zz)
        if k==len(xs)-1 and front_tip: sc=front_tip[0]
        R,_=ring(P,x,t,N,0.5*(k%2),sc)
        rings.append(np.column_stack([np.full(len(R),x),P['spine_y']+side*R[:,0],R[:,1]]))
    V=np.vstack(rings); off=np.cumsum([0]+[len(r) for r in rings])
    panels=[]
    # rear flat face (fan from point 0, all in the plane x=xs[0])
    n0=len(rings[0]); panels.append(('rear-face',[(0,k,k+1) for k in range(1,n0-1)]))
    for a in range(len(rings)-1):
        ia=list(range(off[a],off[a+1])); ib=list(range(off[a+1],off[a+2]))
        T=loft(V,V,ia,ib)
        # orient each triangle consistently later; keep strip order
        panels.append((f'strip-{a+1}',T))
    # front point
    last=rings[-1]; c=last.mean(0); c[0]+=front_tip[1]; V=np.vstack([V,c]); ai=len(V)-1
    il=list(range(off[-2],off[-1]))
    panels.append(('front-cone',[(ai,il[k],il[(k+1)%len(il)]) for k in range(len(il))]))
    faces=[f for _,b in panels for f in b]
    m=trimesh.Trimesh(V,faces,process=False); trimesh.repair.fix_normals(m)
    return m,V,panels,rings

def fold_edges(V,panels):
    """max length of edges that are real folds (>3 deg), and of all edges."""
    faces=[f for _,b in panels for f in b]; m=trimesh.Trimesh(V,faces,process=False)
    ang=np.degrees(m.face_adjacency_angles); e=m.face_adjacency_edges
    L=np.linalg.norm(V[e[:,0]]-V[e[:,1]],axis=1)
    fold=ang>3
    # boundary/seam edges between panels are welds: count them too
    return float(L[fold].max()), float(L.max())

def deck(V,panels,band='strip-3'):
    """the flat top deck quad in a band: the two triangles that use only A/B points"""
    pass
