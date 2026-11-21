# XL125R dash pod as B-rep solids. Built in the 3D viewer's axes (x right, y up, z toward rider,
# front face z=0) then rotated to Fusion Z-up: X right, Y forward, Z up.
import cadquery as cq, math
OW,OH,R=132.0,98.0,14.0
SX=5.0                                  # window centre offset (screen sits right of centre)
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
L=lambda z: cq.Location(cq.Vector(0,0,z))
# main body z -18..0, soft front edge
body=cq.Workplane("XY").workplane(offset=-18).placeSketch(rr(OW,OH,R)).extrude(18)
body=body.faces(">Z").edges().fillet(6)
# curved taper to the back: z -18 -> -30, 132x98 -> 108x74
secs=[]
for i in range(5):
    t=i/4*math.pi/2; ins=24*(1-math.cos(t)); z=-18-12*math.sin(t)
    secs.append(rr(OW-ins,OH-ins,R-5*(1-math.cos(t))).moved(L(z)))
back=cq.Workplane("XY").placeSketch(*secs).loft()
pod=body.union(back)
# screen window with soft recess
win=cq.Workplane("XY").center(SX,0).placeSketch(rr(91,63,5)).extrude(-3).translate((0,0,0.01))
pod=pod.cut(win)
try: pod=pod.faces(">Z").edges(cq.selectors.BoxSelector((SX-46,-32,-0.5),(SX+46,32,0.5))).fillet(1.5)
except Exception as e: print("window fillet skipped",e)
# visor along the top edge, droops toward the rider
vis=(cq.Workplane("YZ").moveTo(0,-8).spline([(0.8,0),(-1.5,9),(-3,16)],includeCurrent=True)
     .lineTo(-4.5,16).spline([(-3.2,8),(-6,-8)],includeCurrent=True).close()
     .extrude(92/2,both=True).translate((0,OH/2-0.5,-4)))
try: vis=vis.edges("|X").fillet(0.6)
except Exception: pass
pod=pod.union(vis)
# bosses + exit spigot on the back
for x in (-30,30): pod=pod.union(cq.Workplane("XY").workplane(offset=-38).center(x,6).circle(6).extrude(9))
pod=pod.union(cq.Workplane("XY").workplane(offset=-40).center(0,-26).circle(9).extrude(11))
pod=pod.cut(cq.Workplane("XY").workplane(offset=-41).center(0,-26).circle(6.5).extrude(12))  # cable bore
for x in (-30,30): pod=pod.cut(cq.Workplane("XY").workplane(offset=-39).center(x,6).circle(2.6).extrude(10))  # M5 tapping holes (placeholder)
# button-head screws (separate bodies)
screws=None
for x,y in ((-57,-39),(57,-39),(-57,39),(57,39)):
    s=cq.Workplane("XY").sphere(3).cut(cq.Workplane("XY").box(10,10,10).translate((0,0,-5))).translate((x,y,0))
    screws=s if screws is None else screws.union(s)
# orange TPU seal line: thin band proud of the body
seal=(cq.Workplane("XY").workplane(offset=-8.2).placeSketch(rr(OW+0.6,OH+0.6,R+0.3)).extrude(1.2)
      .cut(cq.Workplane("XY").workplane(offset=-9).placeSketch(rr(OW-1,OH-1,R-0.5)).extrude(3)))
# screen glass + dark LCD panel in the recess
glass=cq.Workplane("XY").workplane(offset=-3).center(SX,0).placeSketch(rr(90.6,62.6,4.8)).extrude(0.8)
rot=lambda w: w.rotate((0,0,0),(1,0,0),90)
asm=cq.Assembly(name="xl-dash-pod")
asm.add(rot(pod),name="pod_shell",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(seal),name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
asm.add(rot(glass),name="screen",color=cq.Color(0.02,0.02,0.03))
asm.add(rot(screws),name="screws",color=cq.Color(0.1,0.1,0.12))
asm.save("xl-dash-pod.step")
bb=rot(pod).val().BoundingBox();print("pod bbox",round(bb.xmin,1),round(bb.xmax,1),round(bb.ymin,1),round(bb.ymax,1),round(bb.zmin,1),round(bb.zmax,1))
print("valid",rot(pod).val().isValid())
