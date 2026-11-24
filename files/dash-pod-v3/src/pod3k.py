# XL dash pod v3: Waveshare ESP32-S3-Touch-LCD-3.5, cover glass glued flush into the front.
# Built in pod axes (X right, Y up, Z toward rider, glass front ~Z=0), rotated to Fusion Z-up at the end:
# Fusion X right, Y forward, Z up, screen faces -Y.
import cadquery as cq, math, sys
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
def slab(sk,z0,z1,cx=0,cy=0): return cq.Workplane("XY").workplane(offset=z0).center(cx,cy).placeSketch(sk).extrude(z1-z0)
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
GW,GH,GR,GT=92.44,61.00,6.0,1.10        # cover glass (Waveshare drawing)
CLR,GLUE=0.2,0.3                         # glass edge gap, glue bed
WALL=2.5
OW,OH=105.2,GH+2*CLR+2*WALL              # wider for the 99 mm Fowecry MOSFET board
OR=GR+CLR+WALL
ZS=-15.0                                 # front/back split
ZB=-33.5                                 # back face
PD=GT+GLUE                               # glass pocket depth
# LCD module footprint behind the glass, pod axes (board y -> -X, board x -> Y)
LX0,LX1,LY=-38.92,43.92,27.28
# ---------------- FRONT RING ----------------
front=slab(rr(OW,OH,OR),ZS,0).faces(">Z").edges().fillet(1.2)
front=front.cut(slab(rr(GW+2*CLR,GH+2*CLR,GR+CLR),-PD,0.5))                 # glass pocket
front=front.cut(box(LX0-0.6,LX1+1.2,-LY-0.5,LY+0.5,-3.2,-PD+0.01))           # opening through the ledge
front=front.cut(slab(rr(OW-2*WALL-0.6,OH-2*WALL-0.6,OR-WALL),ZS-1,-3.2))      # cavity behind ledge (wall ~2.8)
AX,AY=46.7,26.8                                                              # corner anchor posts for the board arms
for sx in (-1,1):
    for sy in (-1,1):
        front=front.union(cq.Workplane("XY").workplane(offset=ZS).center(sx*AX,sy*AY).circle(3.6).extrude(ZS*-1-8.6))
MX,MY=45.0,21.5                                                              # MOSFET board holes (90 x 43): screw line
CB=[(sx*MX,sy*MY) for sx in (-1,1) for sy in (-1,1)]
# v3g: MOSFET board now lives on the back cover. The pod closes with 4 M3 screws at the corners,
# just outside the MOSFET board's edges, into heat-sets in the front ring's corner posts.
KX,KY=46.7,28.6
CK=[(sx*KX,sy*KY) for sx in (-1,1) for sy in (-1,1)]
for x,y in CK:
    front=front.union(cq.Workplane("XY").workplane(offset=ZS).center(x,y).circle(3.6).extrude(ZS*-1-8.6))
    front=front.cut(cq.Workplane("XY").workplane(offset=ZS-0.1).center(x,y).circle(2.0).extrude(5.6))   # M3 heat-set
# arms with locating pins into the board's 4 M2 holes (72 x 48.5)
HX,HY=36.0,24.25
PCBZ=-6.4-PD                             # board back face (board z -6.4 shifted)
for sx in (-1,1):
    for sy in (-1,1):
        arm=(cq.Workplane("XY").workplane(offset=PCBZ-2.2).moveTo(sx*HX,sy*HY).circle(2.1).extrude(2.2)
             .union(cq.Workplane("XY").workplane(offset=PCBZ-2.2).polyline([(sx*(HX+0.6),sy*(HY-1.8)),(sx*AX,sy*(AY-2.6)),(sx*AX,sy*AY),(sx*(HX+1),sy*(HY+2.4))]).close().extrude(2.2)))
        front=front.union(arm)
        front=front.union(cq.Workplane("XY").workplane(offset=PCBZ).center(sx*HX,sy*HY).circle(0.85).extrude(1.4))
# visor lip over the top edge, toward the rider
vis=(cq.Workplane("YZ").polyline([(OH/2-2.2,-4),(OH/2,-4),(OH/2,0),(OH/2-1.2,11),(OH/2-3.0,11),(OH/2-2.2,0)]).close()
     .extrude(OW/2-6,both=True))
try: vis=vis.edges("|X").fillet(0.5)
except Exception as e: print('vis fillet skip',e)
# v3j: no visor peak (Joel)
# ---------------- BACK COVER ----------------
back=slab(rr(OW,OH,OR),ZB,ZS)
try: back=back.faces("<Z").edges().fillet(6)
except Exception as e: print('back fillet skip',e)
back=back.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZB+2.5,ZS+0.1))
for x,y in CB:   # MOSFET board standoffs, M3 heat-set in the top, board screwed down with M3x6 from inside
    back=back.union(cq.Workplane("XY").workplane(offset=ZB+1).center(x,y).circle(3.6).extrude(-20.6-ZB-1))
    back=back.cut(cq.Workplane("XY").workplane(offset=-20.6-5.6).center(x,y).circle(2.0).extrude(5.7))
for x,y in CK:   # pod closure tubes, M3x25 from the back
    back=back.union(cq.Workplane("XY").workplane(offset=ZB+1).center(x,y).circle(3.4).extrude(ZS-ZB-1.3))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(1.7).extrude(40))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(3.1).extrude(5.5))    # M3 head counterbore
back=back.cut(box(-49.9,49.9,-26.4,26.4,-21.0,ZS+1))        # clear the MOSFET PCB and plug zone
back=back.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZS-1.0,ZS+0.1))  # keep tube tops below the seal face
back=back.union(box(34,44,-7,7,ZB+2,-29.4))   # pad the GPS receiver sticks to
# GPS ceramic antenna pocket in the top wall: wall thinned to 1.6 mm over the antenna
# (size ESTIMATED from Joel's listing photos, scaled off the 12 x 15 board: ~19 x 6 x 5)
back=back.cut(box(-11,11,OH/2-WALL-0.01,OH/2-1.6,-30.0,-21.0))
# TPU seal groove on the back cover's front face
back=back.cut(slab(rr(OW-1.6,OH-1.6,OR-0.8),ZS-1.2,ZS+0.1).cut(slab(rr(OW-4.0,OH-4.0,OR-2.0),ZS-2,ZS+1)))
# fingers that press the board plug home (from the bottom wall)
# (no plug fingers: the MOSFET board's PCB sits 0.5 mm behind the plug and holds it in)
# exit boot and breather vent on the bottom face
by=-OH/2
for x,od,idd in ((-24,13,9.0),(24,12,8.0)):
    back=back.union(cq.Workplane("XZ").workplane(offset=-by).center(x,-24).circle(od/2).extrude(5))
    back=back.cut(cq.Workplane("XZ").workplane(offset=-by+6).center(x,-24).circle(idd/2).extrude(10))
# ---- v3k: SIDE BLOCK on the right for one sealed RECTANGULAR bulkhead plug (size GUESSED: AMPSEAL 23-way style) ----
# Plug: panel cutout 56 (tall) x 20, flange 64 x 26 x 3, rear body 54 x 18 x 22 deep, 2 x M3 flange screws 60 c-c.
SX0=OW/2-WALL-0.5; SW=26.0; SX1=OW/2+SW          # block from inside the pod wall out to the new right face
SZ0,SZ1=ZB,-1.5; SZC=(SZ0+SZ1)/2
side=slab(rr(SX1-SX0,OH,OR),SZ0,SZ1,cx=(SX0+SX1)/2,cy=0)
try: side=side.faces(">Z or <Z").edges().fillet(1.2)
except Exception as e: print('side fillet skip',e)
side=side.cut(box(SX0-1,SX1-WALL,-OH/2+WALL,OH/2-WALL,SZ0+WALL,SZ1-WALL))      # hollow
back=back.union(side)
back=back.cut(box(OW/2-WALL-1,OW/2+0.5,-26,26,ZB+WALL,ZS-1.5))                  # window through the old side wall (wires in)
back=back.cut(box(SX1-WALL-1,SX1+1,-28,28,SZC-10,SZC+10))                       # 56 x 20 plug cutout
for sy in (-1,1):
    back=back.cut(cq.Workplane("YZ").workplane(offset=SX1-6).center(sy*30.0,SZC).circle(1.4).extrude(8))
# mounting bosses on the back (M5 heat-set, 60 c-c like v1/v2)
for x in (-30,30):
    back=back.union(cq.Workplane("XY").workplane(offset=ZB-7).center(x,0).circle(6).extrude(8))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-7.5).center(x,0).circle(3.2).extrude(9))
# ---------------- PARTS INSIDE ----------------
seal=slab(rr(OW-1.8,OH-1.8,OR-0.9),ZS-1.0,ZS+0.4).cut(slab(rr(OW-3.8,OH-3.8,OR-1.9),ZS-2,ZS+1))
board=cq.importers.importStep(SCR+'ws/wsrepo/hardware/mechanical/ESP32-S3-Touch-LCD-3_5.stp')
board=board.rotate((0,0,0),(0,0,1),90).translate((0,0,-PD))
mos=box(-49.5,49.5,-26,26,-20.6,-19.0)
for x,y in CB: mos=mos.cut(cq.Workplane("XY").workplane(offset=-21).center(x,y).circle(1.6).extrude(3))
# GUESSED heights from the listing photos: screw-terminal strips ~10 mm, optos/MOSFETs ~3.5 mm.
# Assumes the yellow jumpers are removed and bridged to H, so the middle is clear for the LiPo.
mos=mos.union(box(-41,41,18,26,-30.6,-20.6))    # top strip: IN1-8, VCC, GND, VIN
mos=mos.union(box(-41,41,-26,-18,-30.6,-20.6))  # bottom strip: OUT1-8 +/-
mos=mos.union(box(-41,41,-17.8,17.8,-24.1,-20.6))  # optos + MOSFETs
parts={
 'lipo_pkcell_1200':    box(-31,31,-17.5,17.5,-29.4,-24.4),
 'gps_receiver_atgm336h': box(33,45,-7.5,7.5,-29.4,-24.4),
 'gps_ceramic_antenna_est': box(-9.5,9.5,26.4,31.4,-28.5,-22.5),
 'mosfet_fowecry_99x52':mos,
 'board_screws_m3x6':  cq.Workplane().add([cq.Workplane('XY').workplane(offset=-19.0).center(x,y).circle(2.75).extrude(2.0).val() for x,y in CB]),
 'bulkhead_rect_guess': box(SX1,SX1+3,-32,32,SZC-13,SZC+13).union(box(SX1-22,SX1,-27,27,SZC-9,SZC+9)),
 'board_plug':          box(-21,21,-30,-19.5,-18.5,-12.95),
}
# ---------------- CHECKS ----------------
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
shell=front.union(back)
bsol=board.val()
print('front valid',front.val().isValid(),'back valid',back.val().isValid())
for n,p in parts.items():
    print('%-22s shell %.1f  board %.1f'%(n,vol(shell,p),vol(cq.Workplane().add(bsol),p)))
    for m,q in parts.items():
        if m>n:
            v=vol(p,q)
            if v>0.01: print('   clash',n,m,round(v,1))
print('board vs shell', round(vol(cq.Workplane().add(bsol),shell),1))
# ---------------- EXPORT ----------------
rot=lambda w: w.rotate((0,0,0),(1,0,0),90)
asm=cq.Assembly(name="xl-dash-pod-v3k")
asm.add(rot(front),name="front_ring",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(back),name="back_cover",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(seal),name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
asm.add(rot(board),name="waveshare_s3_lcd35",color=cq.Color(0.1,0.35,0.2))
cols={'gps_receiver_atgm336h':(0.2,0.45,0.25),'gps_ceramic_antenna_est':(0.75,0.55,0.4),'gps_bn220':(0.2,0.2,0.22),'lipo_pkcell_1200':(0.75,0.75,0.8),'mcp23017_guess':(0.1,0.3,0.7),'gps_bn220':(0.2,0.2,0.22),'buck_pololu':(0.1,0.5,0.2),'mosfet_fowecry_99x52':(0.15,0.25,0.6),'board_plug':(0.05,0.05,0.05),'board_screws_m3x6':(0.7,0.7,0.7),'bulkhead_rect_guess':(0.15,0.15,0.15)}
for n,p in parts.items(): asm.add(rot(p),name=n,color=cq.Color(*cols[n]))
OUT=SCR+'cad3/out11/'
import os; os.makedirs(OUT,exist_ok=True)
asm.save(OUT+'xl-dash-pod-v3k-assembly.step')
for n,w in (('front',front),('back',back),('seal',seal)):
    cq.exporters.export(rot(w),OUT+f'xl-dash-pod-v3k-{n}.step')
    cq.exporters.export(rot(w),OUT+f'xl-dash-pod-v3k-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(rot(w),OUT+f'part-{n}.stl')
cq.exporters.export(rot(board),OUT+'part-board.stl',tolerance=0.1,angularTolerance=0.3)
bb=rot(shell).val().BoundingBox();print('pod bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f'%(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax))
