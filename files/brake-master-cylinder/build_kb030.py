# Mock-up of Righetti Ridolfi KB030 kart brake master cylinder (22.2 mm bore)
# Dimensions read from Righetti drawing KB030; unlabelled features scaled off the drawing (+-1-2 mm).
# Axes: X along body (0 = boot tip, +X towards outlet), Y across, Z up (0 = body underside). mm.
import cadquery as cq, math
R=15.0; ZC=15.0          # body radius (30 wide), bore axis height
def cylx(x0,x1,r,z=ZC):
    return cq.Workplane("YZ").workplane(offset=x0).center(0,z).circle(r).extrude(x1-x0)
# boot (bellows simplified as stacked rings)
boot=cylx(0,14,7.5)
for i,x in enumerate([1.5,5.5,9.5]):
    boot=boot.union(cylx(x,x+2.5,9.3))
# front housing (holds arm/plunger) x 14-50.5, top z 47.3
house=cylx(14,50.5,R).union(cq.Workplane("XY").box(36.5,30,32.3,centered=(False,True,False)).translate((14,0,15)))
# flange ring at 49.5-51
house=house.union(cylx(49.5,51.5,15.8))
# main block x 50.5-131.5, top z 40
block=cylx(50.5,131.5,R).union(cq.Workplane("XY").box(81,30,25,centered=(False,True,False)).translate((50.5,0,15)))
# reservoir: loft from block top to wider tub, then tub to 71.1
lo=cq.Workplane("XY").workplane(offset=40).center(90.75,0).rect(81,30)
res=(cq.Workplane("XY").workplane(offset=40).center(90.75,0).rect(79,30)
     .workplane(offset=18.6).center(5.3,0).rect(84,35).loft())
tub=cq.Workplane("XY").box(84,35,12.5,centered=(False,True,False)).translate((54.4,0,58.6)).edges("|Z").fillet(4)
lid=cq.Workplane("XY").box(84,35,1.0,centered=(False,True,False)).translate((54.4,0,64.5)).edges("|Z").fillet(4)
res=res.union(tub)
# end cap + outlet hex
cap=cq.Workplane("XY").box(3,30,30,centered=(False,True,False)).translate((131.5,0,0))
hexo=cq.Workplane("YZ").workplane(offset=134.5).center(0,ZC).polygon(6,19/math.cos(math.pi/6)).extrude(4.5)
body=boot.union(house).union(block).union(res).union(cap).union(hexo)
# transverse mounting holes d6.3, c'bore d10.6 x5 on -Y side, at X 62.8 / 97.8, Z 33.7
for x in (62.8,97.8):
    body=body.cut(cq.Workplane("XZ").workplane(offset=-20).center(x,33.7).circle(3.15).extrude(-40,both=False) if False else
                  cq.Workplane("XZ",origin=(0,20,0)).center(x,33.7).circle(3.15).extrude(40))
    body=body.cut(cq.Workplane("XZ",origin=(0,-10,0)).center(x,33.7).circle(5.3).extrude(5.1))
# bore (blind, for show) and outlet M10 hole
body=body.cut(cylx(14,125,11.1).translate((0,0,0)).intersect(cylx(51,125,11.1)))
body=body.cut(cylx(133,139.1,5.0))
# slave arm: 5 mm plate, outline from drawing; holes d6.1
pts=[(22.7,47.3),(26.0,60.0),(32.0,74.0),(36.5,83.0),(41.0,89.6),(46.5,89.0),(50.5,85.0),(51.0,79.5),(38.5,47.3)]
arm=cq.Workplane("XZ").polyline(pts).close().extrude(2.5,both=True)
for (x,z) in ((43.0,82.0),(32.7,65.1)):
    arm=arm.cut(cq.Workplane("XZ",origin=(0,10,0)).center(x,z).circle(3.05).extrude(20))
# clevis base on housing
base=cq.Workplane("XY").box(16,12,3,centered=(False,True,False)).translate((22.7,0,47.3))
mc=body.union(arm).union(base)
cq.exporters.export(mc,"righetti-kb030-mockup.step")
cq.exporters.export(mc,"righetti-kb030-mockup.stl",tolerance=0.05,angularTolerance=0.1)
bb=mc.val().BoundingBox(); print(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)
