import trimesh, numpy as np, json
from shapely.geometry import Polygon
from shapely.ops import unary_union
a2=trimesh.load('arm_armcoords.stl')
polys=[]
for x0 in np.arange(-12,28,2):
    s=a2.section(plane_origin=(x0,0,0),plane_normal=(1,0,0))
    if s is None: continue
    for e in s.discrete:
        p=Polygon(np.c_[e[:,2]+5.8,e[:,1]-0.1])  # model lug hole 194.2/-49.9 -> bench lug 200/-50
        if p.is_valid and p.area>50 and p.bounds[0]>60 and p.bounds[2]<300: polys.append(p.buffer(0))
u=unary_union(polys).simplify(0.3)
geoms=list(u.geoms) if hasattr(u,'geoms') else [u]
for g in geoms: print(g.bounds, g.area, len(g.interiors))
json.dump([[list(map(lambda v:round(v,1),c)) for c in g.exterior.coords] for g in geoms], open('/home/claude/chassis-bench/files/rocker-mockup/arm_section_rocker_band.json','w'))
