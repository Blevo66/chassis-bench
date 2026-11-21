import cadquery as cq
W,H,T=211.0,124.7,8.0  # Galaxy Tab A9 (8.7"), landscape. Fusion axes: X right, Y forward, Z up; screen faces -Y (rider)
b=cq.Workplane("XZ").sketch().rect(W,H).vertices().fillet(9).finalize().extrude(T)  # XZ normal is -Y: extrudes toward rider
b=b.edges().fillet(1.5)
scr=cq.Workplane("XZ").workplane(offset=T).rect(189.8,113.3).extrude(0.3)
a=cq.Assembly(name="galaxy-tab-a9-rough");a.add(b,name="body",color=cq.Color(0.25,0.27,0.3));a.add(scr,name="screen",color=cq.Color(0.02,0.02,0.03))
a.save("galaxy-tab-a9-rough.step");bb=b.val().BoundingBox();print(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)
