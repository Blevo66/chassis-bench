"""v7 simple: big flat folded panels (straight-folded sections like v3), 80 mm flat rear face for the seat,
flat top deck with the filler pad, and a short pointed front made of triangles (no flat front).
Sections keep parallel edges at every station (scaling keeps edge directions), so every side face is one flat panel."""
import numpy as np, trimesh, tank, tri3

def build(P,side=1,N=None,xs=(20,80,290,345),rear_h=80.,front_tip=(0.55,14.)):
    xr,xf=P['x_rear'],P['x_front']; rings=[]
    for k,x in enumerate(xs):
        t=(x-xr)/(xf-xr); s={kk:P['rear'][kk]+(P['front'][kk]-P['rear'][kk])*t for kk in P['front']}
        S=tank.section(s,P); C=S.mean(0); sc=1.0
        if k==0: sc=rear_h/np.ptp(S[:,1])
        if k==len(xs)-1: sc=front_tip[0]
        S=(S-C)*sc+C
        rings.append(np.column_stack([np.full(len(S),x),P['spine_y']+side*S[:,0],S[:,1]]))
    V=np.vstack(rings); n=len(rings[0]); panels=[]
    panels.append(('rear-face',[(0,k,k+1) for k in range(1,n-1)]))
    for a in range(len(rings)-1):
        T=[]
        for k in range(n):
            k2=(k+1)%n; i0,i1,j0,j1=a*n+k,a*n+k2,(a+1)*n+k,(a+1)*n+k2
            T+=[(i0,j0,j1),(i0,j1,i1)]
        panels.append((f'strip-{a+1}',T))
    c=rings[-1].mean(0); c[0]+=front_tip[1]; V=np.vstack([V,c]); ai=len(V)-1; base=(len(rings)-1)*n
    fan=[(ai,base+k,base+(k+1)%n) for k in range(n)]
    h=n//2
    panels.append(('front-cone-top',fan[:h])); panels.append(('front-cone-bottom',fan[h:]))   # two pieces so each lies flat
    faces=[f for _,b in panels for f in b]
    m=trimesh.Trimesh(V,faces,process=False); trimesh.repair.fix_normals(m)
    return m,V,panels,rings
