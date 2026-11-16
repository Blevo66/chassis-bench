"""v9: bigger, irregular triangles from the section's own corners (crisp, no fillets), long edges split
at uneven points that change from station to station, flat top deck (filler) and FLAT BOTTOM on each pod
(the bottom edge E-F is never split, so the bottom of each band is one flat panel), 80 mm rear face, short pointed front."""
import numpy as np, trimesh, tank, tri3

# uneven split fractions per station (deterministic, so the pattern stays the same between runs)
JIT=[(0.42,),(0.61,),(0.35,0.7),(0.55,),(0.3,0.66)]

def ring_pts(S,k,Lmax):
    """section corners A..I plus uneven extra points on long edges, except the top deck A-B and bottom E-F"""
    n=len(S); out=[]; tags=[]
    for i in range(n):
        p,q=S[i],S[(i+1)%n]; out.append(p); tags.append(i)
        if i in (0,4): continue                      # A-B top deck and E-F bottom stay flat
        L=np.linalg.norm(q-p)
        if L>Lmax:
            m=int(np.ceil(L/Lmax))-1
            fr=JIT[(k+i)%len(JIT)]
            fr=fr[:m] if len(fr)>=m else tuple(np.linspace(0,1,m+2)[1:-1])
            for f in fr: out.append(p+(q-p)*f); tags.append(i+0.5)
    return np.array(out)

def build(P,side=1,xs=(20,140,260,345),Lmax=170.,rear_h=80.,front_tip=(0.6,12.),split_cone=True):
    xr,xf=P['x_rear'],P['x_front']; rings=[]
    for k,x in enumerate(xs):
        t=(x-xr)/(xf-xr); s={kk:P['rear'][kk]+(P['front'][kk]-P['rear'][kk])*t for kk in P['front']}
        S=tank.section(s,P); C=S.mean(0); sc=1.0
        if k==0: sc=rear_h/np.ptp(S[:,1])
        if k==len(xs)-1: sc=front_tip[0]
        S=(S-C)*sc+C
        R=ring_pts(S,k,Lmax*sc if sc<1 else Lmax)
        rings.append(np.column_stack([np.full(len(R),x),P['spine_y']+side*R[:,0],R[:,1]]))
    V=np.vstack(rings); off=np.cumsum([0]+[len(r) for r in rings]); panels=[]
    n0=len(rings[0]); panels.append(('rear-face',[(0,k,k+1) for k in range(1,n0-1)]))
    for a in range(len(rings)-1):
        ia=list(range(off[a],off[a+1])); ib=list(range(off[a+1],off[a+2]))
        panels.append((f'strip-{a+1}',tri3.loft(V,V,ia,ib)))
    last=rings[-1]; c=last.mean(0); c[0]+=front_tip[1]; V=np.vstack([V,c]); ai=len(V)-1
    il=list(range(off[-2],off[-1])); fan=[(ai,il[k],il[(k+1)%len(il)]) for k in range(len(il))]
    if split_cone:
        h=len(fan)//2; panels.append(('front-cone-top',fan[:h])); panels.append(('front-cone-bottom',fan[h:]))
    else: panels.append(('front-cone',fan))
    m=trimesh.Trimesh(V,[f for _,b in panels for f in b],process=False); trimesh.repair.fix_normals(m)
    return m,V,panels,rings
