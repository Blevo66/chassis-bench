"""Builds the twin half-saddle tank: mock-up STLs, flat patterns (DXF), renders, info JSON."""
import numpy as np, trimesh, json, os, sys, ezdxf
import tank
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
P=tank.P; T=float(os.environ.get('T','1.2'))   # sheet thickness mm

def sec3(x,key,side):
    S=tank.section(P[key],P); return np.array([[x,P['spine_y']+side*y,z] for y,z in S])
import shapely.geometry as sg

# ---------- unfold a strip of planar quads ----------
def place(a2,b2,a,b,c,ref2=None):
    """2D position of 3D point c given edge a-b placed at a2-b2; put on side opposite ref2."""
    e=b-a; L=np.linalg.norm(e); u=e/L
    t=np.dot(c-a,u); h=np.linalg.norm((c-a)-t*u)
    e2=(b2-a2)/np.linalg.norm(b2-a2); n2=np.array([-e2[1],e2[0]])
    p=a2+t*e2+h*n2
    if ref2 is not None and np.dot(ref2-a2,n2)>0: p=a2+t*e2-h*n2
    return p

def unfold(F,R,idx):
    """F,R: front/rear 3D section points; idx: ordered vertex indices of the strip edges (len n+1 for n faces).
    Returns outline polygon (2D) and bend lines."""
    a,b=F[idx[0]],R[idx[0]]
    L=np.linalg.norm(b-a); A2={('F',idx[0]):np.array([0.,0.]),('R',idx[0]):np.array([L,0.])}
    prev_ref=None; bends=[]; angles=[]
    for k in range(len(idx)-1):
        i,j=idx[k],idx[k+1]
        a2,b2=A2[('F',i)],A2[('R',i)]
        cF=place(a2,b2,F[i],R[i],F[j],prev_ref); cR=place(a2,b2,F[i],R[i],R[j],prev_ref)
        A2[('F',j)]=cF; A2[('R',j)]=cR
        if k>0:
            # convex (outside corner) or concave (inside corner: folds the opposite way)
            h0=idx[k-1]; d0=F[i]-F[h0]; d1=F[j]-F[i]
            cz=(d0[1]*d1[2]-d0[2]*d1[1])*np.sign(F[0,1]-P['spine_y'])
            bends.append((a2,b2,'outside' if cz<0 else 'INSIDE - fold opposite way'))
            n0=np.cross(R[idx[k-1]]-F[idx[k-1]],F[i]-F[idx[k-1]]); n1=np.cross(R[i]-F[i],F[j]-F[i])
            angles.append(np.degrees(np.arccos(np.clip(np.dot(n0,n1)/np.linalg.norm(n0)/np.linalg.norm(n1),-1,1))))
        prev_ref=(a2+b2)/2
    outline=[A2[('F',i)] for i in idx]+[A2[('R',i)] for i in idx[::-1]]
    return np.array(outline),bends,angles

parts={}
side=+1  # left half; right half is the mirror image (flip the flat patterns)
xf,xr=P['x_front'],P['x_rear']
# skins stop T short of each end so they butt onto the end plates
F=sec3(xf-T,'front',side); R=sec3(xr+T,'rear',side)
# section idx: 0 A inner top,1 B,2 C,3 D,4 E,5 F,6 H,7 I
def check(F,R,idx,res):
    poly=res[0]; n=len(idx)
    for k,i in enumerate(idx):
        a2,b2=poly[k],poly[2*n-1-k]
        assert abs(np.linalg.norm(a2-b2)-np.linalg.norm(F[i]-R[i]))<1e-6
    for k in range(n-1):
        i,j=idx[k],idx[k+1]
        assert abs(np.linalg.norm(poly[k]-poly[k+1])-np.linalg.norm(F[i]-F[j]))<1e-6
        assert abs(np.linalg.norm(poly[2*n-1-k]-poly[2*n-2-k])-np.linalg.norm(R[i]-R[j]))<1e-6
        assert abs(np.linalg.norm(poly[k]-poly[2*n-2-k])-np.linalg.norm(F[i]-R[j]))<1e-6  # diagonal
    return res
parts['outer_skin']=check(F,R,[0,1,2,3,4],unfold(F,R,[0,1,2,3,4]))     # top, shoulder, side, lower chamfer
parts['inner_pan']=check(F,R,[4,5,6,7,0],unfold(F,R,[4,5,6,7,0]))   # bottom, inner chamfer, lower inner wall, slope, spine wall
def plate(key):
    S=tank.section(P[key],P); S=S-S.mean(0); return S
parts['front_plate']=(plate('front'),[],[]); parts['rear_plate']=(plate('rear'),[],[])
# baffle at mid length, inset 2 mm, 3 holes
mid={k:(P['front'][k]+P['rear'][k])/2 for k in P['front']}
Sm=tank.section({k:float(v) for k,v in mid.items()},P)
cen=Sm.mean(0)
pb=sg.Polygon(Sm).buffer(-2,join_style=2)   # 2 mm smaller all round
pb=pb.difference(sg.Point(mid['yl'],mid['zb']).buffer(14)).difference(sg.Point((mid['yo']+mid['yl'])/2,mid['zb']).buffer(10))  # drain notches at the bottom so fuel reaches the tap
Sb=np.array(pb.exterior.coords)[:-1]
holes=[]
yc=(mid['yl']+mid['yo'])/2
for z in np.linspace(mid['zb']+20, mid['zt']-20, 9):
    for y in (yc, (P['inner_gap']+mid['yo'])/2):
        c=sg.Point(y,z)
        if pb.contains(c) and pb.exterior.distance(c)>14+8 and all(np.hypot(y-h[0],z-h[1])>2*14+10 for h in holes): holes.append((y,z))
parts['baffle']=(Sb-cen,[],[]); baffle_holes=[(np.array(h)-cen) for h in holes]

# ---------- DXF + summary ----------
info={'sheet_mm':T,'parts':{}}
for name,(poly,bends,angles) in parts.items():
    doc=ezdxf.new('R2010'); msp=doc.modelspace()
    doc.layers.add('CUT',color=1); doc.layers.add('BEND',color=5); doc.layers.add('NOTE',color=3)
    msp.add_lwpolyline([tuple(p) for p in poly],close=True,dxfattribs={'layer':'CUT'})
    for (a,b,kind),ang in zip(bends,angles):
        msp.add_line(tuple(a),tuple(b),dxfattribs={'layer':'BEND'})
        m=(a+b)/2; msp.add_text(f'BEND {ang:.0f} deg {kind}',dxfattribs={'layer':'NOTE','height':6}).set_placement(tuple(m))
    if name=='baffle':
        for c in baffle_holes:
            msp.add_circle(tuple(c),14,dxfattribs={'layer':'CUT'})
    msp.add_text(f'{name} - XL125R twin tank LEFT half (mirror for RIGHT) - {T} mm mild steel - make 2 (1 L + 1 R)',dxfattribs={'layer':'NOTE','height':7}).set_placement((poly[:,0].min(),poly[:,1].min()-20))
    doc.saveas(f'{OUT}/flat-{name.replace("_","-")}.dxf')
    area=trimesh.path.polygons.Polygon(poly).area
    w,h=np.ptp(poly[:,0]),np.ptp(poly[:,1])
    info['parts'][name]={'flat_size_mm':[round(w),round(h)],'area_mm2':round(area),'bend_angles_deg':[round(a,1) for a in angles],'bend_kind':[b[2] for b in bends]}
area=sum(v['area_mm2'] for v in info['parts'].values())
info['steel_kg_per_half']=round(area*T*7.85e-6,2); info['steel_kg_both']=round(2*area*T*7.85e-6,2)

# ---------- 3D: halves, mockup split ----------
L=tank.half_mesh(P,+1); Rm=tank.half_mesh(P,-1)
info['litres_per_half']=round(L.volume/1e6,2); info['litres_total_gross']=round(2*L.volume/1e6,2)
L.export(f'{OUT}/tank-left-half.stl'); Rm.export(f'{OUT}/tank-right-half.stl')
(L+Rm).export(f'{OUT}/tank-both-halves-on-frame-coords.stl')
xs=(xf+xr)/2; zcut=float(os.environ.get('ZCUT','400'))
for nm,m in (('left',L),('right',Rm)):
    a=m.slice_plane([xs,0,0],[1,0,0],cap=True); b=m.slice_plane([xs,0,0],[-1,0,0],cap=True)
    pieces=[('rear',b)]
    pieces+=[('front-upper',a.slice_plane([0,0,zcut],[0,0,1],cap=True)),('front-lower',a.slice_plane([0,0,zcut],[0,0,-1],cap=True))]
    for part,pm in pieces:
        pm=pm.copy()
        # lay it on its biggest flat face, then spin flat on the bed to fit
        best=None
        for fi,fn in enumerate(pm.facets_normal):
            T_=trimesh.geometry.align_vectors(fn,[0,0,-1]); q=pm.copy(); q.apply_transform(T_)
            for ang in np.radians(np.arange(0,180,5)):
                q2=q.copy(); q2.apply_transform(trimesh.transformations.rotation_matrix(ang,[0,0,1]))
                e=q2.extents
                if e[0]<=250 and e[1]<=250 and e[2]<=250:
                    score=(pm.facets_area[fi], -e[2])
                    if best is None or score>best[0]: best=(score,q2)
                    break
        assert best is not None, (nm,part,pm.extents)
        q=best[1]; q.apply_translation(-q.bounds[0])
        q.export(f'{OUT}/mockup-{nm}-{part}.stl')
        info.setdefault('mockup_print_sizes_mm',{})[f'{nm}-{part}']=[round(x) for x in q.extents]
fr=sec3(xf,'front',1); rr=sec3(xr,'rear',1)
info['front_section_left_yz']=tank.section(P['front'],P).round(1).tolist()
info['rear_section_left_yz']=tank.section(P['rear'],P).round(1).tolist()
info['params']=P
info['max_width_mm']=round(2*(P['front']['yo']+0))
json.dump(info,open(f'{OUT}/tank-info.json','w'),indent=1)
print(json.dumps({k:v for k,v in info.items() if k!='params'},indent=1))
