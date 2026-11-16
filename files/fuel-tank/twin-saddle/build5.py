"""v4 low-poly build: mesh, panels (ring strips + caps + baffle), DXF, mock-up STLs, info."""
import numpy as np, trimesh, json, os, sys, ezdxf, shapely.geometry as sg, shapely.ops as so
import tank, tri, tri2
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
P=tank.P; T=float(os.environ.get('T','1.2')); NAR=int(os.environ.get('NAR','9'))
TIP=float(os.environ.get('TIP','60')); TS=float(os.environ.get('TS','0.5')); AO=float(os.environ.get('AO','20'))
info={'sheet_mm':T,'version':'v5 big crisp triangles, pointed ends','parts':{}}
meshes={}
for side,nm in ((1,'left'),(-1,'right')):
    st=tri2.stations(P,TIP,TS)
    rings,ap=tri2.build(P,side,NAR,st,AO)
    m,V,panels=tri2.mesh(rings,ap)
    meshes[nm]=(m,V,panels,rings)
m,V,panels,rings=meshes['left']
bands=[b for _,b in panels]
info['stations_x']=[round(float(r[0,0])) for r in rings]; info['points_round']=NAR
info['max_triangle_side_mm']=round(tri2.max_edge(V,panels),1)
info['triangles_per_half']=sum(len(b) for b in bands)
info['litres_per_half']=round(m.volume/1e6,2); info['litres_total_gross']=round(2*m.volume/1e6,2)
fn=m.face_normals
def fold_kind(f1i,f2,sh):
    n=fn[f1i]; o=[v for v in f2 if v not in sh][0]
    return 'out' if np.dot(V[o]-V[sh[0]],n)<0 else 'IN'
area_total=0; fi0=0
def save_dxf(name,poly,folds=(),holes=(),note=''):
    doc=ezdxf.new('R2010'); msp=doc.modelspace()
    for L_,c in (('CUT',1),('ETCH_FOLD',5),('NOTE',3)): doc.layers.add(L_,color=c)
    msp.add_lwpolyline(list(poly.exterior.coords),close=True,dxfattribs={'layer':'CUT'})
    for h in holes: msp.add_circle(h[0],h[1],dxfattribs={'layer':'CUT'})
    for a,b,ang,kind in folds:
        if ang<3: continue          # under 3 deg: leave flat, the weld pulls it in
        msp.add_line(tuple(a),tuple(b),dxfattribs={'layer':'ETCH_FOLD'})
        mm=(a+b)/2; msp.add_text(f'{ang:.0f} {kind}',dxfattribs={'layer':'NOTE','height':5}).set_placement(tuple(mm))
    x0,y0,_,_=poly.bounds
    msp.add_text(f'{name} - LEFT half (mirror for RIGHT) - {T} mm mild steel - {note}',dxfattribs={'layer':'NOTE','height':7}).set_placement((x0,y0-15))
    doc.saveas(f'{OUT}/flat-{name}.dxf')
flats={}
for bi,(pname,band) in enumerate(panels):
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
    name=pname
    note='cone at the rear tip' if pname=='rear-cone' else 'cone at the front tip' if pname=='front-cone' else f'ring strip between x={info["stations_x"][bi-1]} and x={info["stations_x"][bi]} from pivot'
    save_dxf(name,u,fk,note=note+'; closes on itself at the inner top edge')
    flats[name]=(u,fk)
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
