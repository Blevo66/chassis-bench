"""v4 low-poly build: mesh, panels (ring strips + caps + baffle), DXF, mock-up STLs, info."""
import numpy as np, trimesh, json, os, sys, ezdxf, shapely.geometry as sg, shapely.ops as so
import tank, tri, tri3, tri5, copy, shapely
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
P=copy.deepcopy(tank.P); P['rear']['yo']=140.; P['rear']['c']=14.; P['front']['c']=22.
for _k in ('zb','yo','zt'):
    for _e,_s in (('F','front'),('R','rear')):
        if os.environ.get(_k.upper()+_e): P[_s][_k]=float(os.environ[_k.upper()+_e])
T=float(os.environ.get('T','1.2')); NAR=int(os.environ.get('NAR','6'))
XS=tuple(int(v) for v in os.environ.get('XS','20,140,260,345').split(',')); FT=(float(os.environ.get('FTS','0.6')),float(os.environ.get('FTO','12'))); PADBAND=int(os.environ.get('PADBAND','1'))
info={'sheet_mm':T,'version':'v9 bigger irregular facets, flat pod bottoms, flat filler deck, 80 mm rear face','parts':{}}
meshes={}
for side,nm in ((1,'left'),(-1,'right')):
    m,V,panels,rings=tri5.build(P,side,xs=XS,Lmax=float(os.environ.get('LMAX','200')),front_tip=FT)
    meshes[nm]=(m,V,panels,rings)
m,V,panels,rings=meshes['left']
bands=[b for _,b in panels]
info['stations_x']=list(XS); info['points_round']=NAR
fe,al=tri3.fold_edges(V,panels); info['longest_fold_line_mm']=round(fe,1); info['note_edges']='limit for fold lines raised to 200 mm (Joel, 16 Nov); the flat deck diagonal and the rear face are not folds'
info['triangles_per_half']=sum(len(b) for b in bands); info['flat_faces_per_half']=len(m.facets)+len([f for f in range(len(m.faces)) if f not in set(np.concatenate(m.facets)) ]) if len(m.facets) else len(m.faces)
info['litres_per_half']=round(m.volume/1e6,2); info['litres_total_gross']=round(2*m.volume/1e6,2)
fn=m.face_normals
def fold_kind(f1i,f2,sh):
    n=fn[f1i]; o=[v for v in f2 if v not in sh][0]
    return 'out' if np.dot(V[o]-V[sh[0]],n)<0 else 'IN'
area_total=0; fi0=0
def save_dxf(name,poly,folds=(),holes=(),note='',pad=None):
    doc=ezdxf.new('R2010'); msp=doc.modelspace()
    for L_,c in (('CUT',1),('ETCH_FOLD',5),('NOTE',3)): doc.layers.add(L_,color=c)
    msp.add_lwpolyline(list(poly.exterior.coords),close=True,dxfattribs={'layer':'CUT'})
    for h in holes: msp.add_circle(h[0],h[1],dxfattribs={'layer':'CUT'})
    for a,b,ang,kind in folds:
        if ang<3: continue          # under 3 deg: leave flat, the weld pulls it in
        msp.add_line(tuple(a),tuple(b),dxfattribs={'layer':'ETCH_FOLD'})
        mm=(a+b)/2; msp.add_text(f'{ang:.0f} {kind}',dxfattribs={'layer':'NOTE','height':5}).set_placement(tuple(mm))
    if pad is not None:
        msp.add_circle(tuple(pad),50,dxfattribs={'layer':'ETCH_FOLD'})
        msp.add_text('FILLER PAD 100 dia (cut the hole to suit your neck)',dxfattribs={'layer':'NOTE','height':5}).set_placement((pad[0]-45,pad[1]))
    x0,y0,_,_=poly.bounds
    msp.add_text(f'{name} - LEFT half (mirror for RIGHT) - {T} mm mild steel - {note}',dxfattribs={'layer':'NOTE','height':7}).set_placement((x0,y0-15))
    doc.saveas(f'{OUT}/flat-{name}.dxf')
flats={}
# filler pad on the flat deck of strip-3 (x 150-265)
Q=np.array([rings[PADBAND][0],rings[PADBAND][1],rings[PADBAND+1][1],rings[PADBAND+1][0]])
nq=np.cross(Q[1]-Q[0],Q[3]-Q[0]); nq/=np.linalg.norm(nq); uq=(Q[1]-Q[0])/np.linalg.norm(Q[1]-Q[0]); wq=np.cross(nq,uq)
dpoly=sg.Polygon([((q-Q[0])@uq,(q-Q[0])@wq) for q in Q]); mic=shapely.maximum_inscribed_circle(dpoly)
c2=np.array(mic.coords[0]); pad3=Q[0]+c2[0]*uq+c2[1]*wq
info['filler_pad']={'centre_xyz_left':[round(v) for v in pad3],'deck_inscribed_dia_mm':round(2*mic.length),'cap_space_dia_mm':100}
for bi,(pname,band) in enumerate(panels):
    if pname=='rear-face':
        R0=rings[0]; poly=sg.Polygon(R0[:,1:]); poly=sg.Polygon(np.array(poly.exterior.coords)-np.array(poly.centroid.coords[0]))
        save_dxf('rear-face',poly,note='flat vertical rear face, 80 mm tall, the seat runs up to it'); flats['rear-face']=(poly,[])
        info['parts']['rear-face']={'flat_size_mm':[round(v) for v in (poly.bounds[2]-poly.bounds[0],poly.bounds[3]-poly.bounds[1])],'area_mm2':round(poly.area)}
        area_total+=poly.area; fi0+=len(band); continue
    tris2,folds=tri.unfold_band(V,band)
    polys=[sg.Polygon(t) for t in tris2]
    u=so.unary_union([p.buffer(0.05,join_style=2) for p in polys]).buffer(-0.05,join_style=2)
    if u.geom_type!='Polygon': u=max(u.geoms,key=lambda g:g.area)
    u=u.simplify(0.02)
    overlap=sum(p.area for p in polys)-u.area
    # fold kinds
    fk=[]
    for k in range(1,len(band)):
        sh=[v for v in band[k] if v in band[k-1]]
        fk.append((folds[k-1][0],folds[k-1][1],folds[k-1][2],fold_kind(fi0+k-1,band[k],sh)))
    fi0+=len(band)
    # rotate so the strip lies along X (minimum rotated rectangle)
    mrr=u.minimum_rotated_rectangle; c=np.array(mrr.exterior.coords)[:4]
    e=c[1]-c[0] if np.linalg.norm(c[1]-c[0])>np.linalg.norm(c[2]-c[1]) else c[2]-c[1]
    ang=-np.arctan2(e[1],e[0]); R=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]])
    from shapely import affinity
    u=affinity.rotate(u,ang,origin=(0,0),use_radians=True); fk=[(R@a,R@b,an,kd) for a,b,an,kd in fk]
    padmark=None
    if pname==f'strip-{PADBAND+1}':
        for f3,t2 in zip(band,tris2):
            A3=V[list(f3)]; 
            M=np.column_stack([A3[1]-A3[0],A3[2]-A3[0]]); lam,res,_,_=np.linalg.lstsq(M,pad3-A3[0],rcond=None)
            if lam.min()>=-1e-6 and lam.sum()<=1+1e-6 and np.linalg.norm(M@lam-(pad3-A3[0]))<0.5:
                t2=np.array(t2); padmark=R@(t2[0]+lam[0]*(t2[1]-t2[0])+lam[1]*(t2[2]-t2[0])); break
    name=pname
    note='front point, '+pname.split('-')[-1]+' piece' if pname.startswith('front-cone') else f'ring strip between x={XS[bi-1]} and x={XS[bi]} from pivot'
    save_dxf(name,u,fk,note=note+'; closes on itself at the inner top edge',pad=padmark)
    flats[name]=(u,fk) if padmark is None else (u,fk,[],padmark)
    info['parts'][name]={'flat_size_mm':[round(v) for v in (u.bounds[2]-u.bounds[0],u.bounds[3]-u.bounds[1])],'folds':len(fk),
        'fold_angles_deg':[round(f[2],1) for f in fk],'overlap_mm2':round(overlap,1),'area_mm2':round(u.area)}
    area_total+=u.area
# baffle at mid length
xm=(P['x_front']+P['x_rear'])/2
sec=m.section(plane_origin=[xm,0,0],plane_normal=[1,0,0]); pts=sec.vertices[:,1:]
pl=sg.MultiPoint(pts)  # build polygon from section path
path2,_=sec.to_planar(normal=[1,0,0]) if False else (None,None)
loops=[np.array(e) for e in sec.discrete]; loop=max(loops,key=len)[:,1:]
pb=sg.Polygon(loop).buffer(-2,join_style=2); pb=sg.Polygon(np.array(pb.exterior.coords)-np.array(pb.centroid.coords[0]))
minx,miny,maxx,maxy=pb.bounds
pb=pb.difference(sg.Point(np.array(pb.exterior.coords)[np.argmin(np.array(pb.exterior.coords)[:,1])]).buffer(14))  # drain notch at the lowest corner
holes=[]
for z in np.linspace(miny+40,maxy-30,10):
    for y in np.linspace(minx+25,maxx-25,4):
        c=sg.Point(y,z)
        if pb.contains(c) and pb.exterior.distance(c)>14+8 and all(np.hypot(y-h[0][0],z-h[0][1])>2*14+10 for h in holes): holes.append(((y,z),14))
save_dxf('baffle',pb,holes=holes,note=f'baffle at x={xm:.0f}, tack in before closing'); flats['baffle']=(pb,[],holes)
info['parts']['baffle']={'flat_size_mm':[round(maxx-minx),round(maxy-miny)],'holes':len(holes)}
area_total+=pb.area
info['steel_kg_per_half']=round(area_total*T*7.85e-6,2); info['steel_kg_both']=round(2*area_total*T*7.85e-6,2)
# 3D outputs
L=meshes['left'][0]; Rm=meshes['right'][0]
L.export(f'{OUT}/tank-left-half.stl'); Rm.export(f'{OUT}/tank-right-half.stl'); (L+Rm).export(f'{OUT}/tank-both-halves-on-frame-coords.stl')
xs=(P['x_front']+P['x_rear'])/2; zcut=float(os.environ.get('ZCUT','340'))
for nm,mm in (('left',L),('right',Rm)):
    a=mm.slice_plane([xs,0,0],[1,0,0],cap=True); b=mm.slice_plane([xs,0,0],[-1,0,0],cap=True)
    pieces=[('rear',b),('front-upper',a.slice_plane([0,0,zcut],[0,0,1],cap=True)),('front-lower',a.slice_plane([0,0,zcut],[0,0,-1],cap=True))]
    for part,pm in pieces:
        best=None
        for fi_,fnrm in enumerate(pm.facets_normal):
            T_=trimesh.geometry.align_vectors(fnrm,[0,0,-1]); q=pm.copy(); q.apply_transform(T_)
            for an in np.radians(np.arange(0,180,5)):
                q2=q.copy(); q2.apply_transform(trimesh.transformations.rotation_matrix(an,[0,0,1])); e=q2.extents
                if max(e)<=250:
                    sc=(pm.facets_area[fi_],-e[2])
                    if best is None or sc>best[0]: best=(sc,q2)
                    break
        assert best is not None,(nm,part,pm.extents)
        q=best[1]; q.apply_translation(-q.bounds[0]); q.export(f'{OUT}/mockup-{nm}-{part}.stl')
        info.setdefault('mockup_print_sizes_mm',{})[f'{nm}-{part}']=[round(x) for x in q.extents]
info['params']=P
json.dump(info,open(f'{OUT}/tank-info.json','w'),indent=1)
import pickle; pickle.dump(flats,open(f'{OUT}/.flats.pkl','wb'))
print(json.dumps({k:v for k,v in info.items() if k not in ('params',)},indent=0)[:3000])
