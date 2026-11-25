# XL dash pod v3: Waveshare ESP32-S3-Touch-LCD-3.5, cover glass glued flush into the front.
# Built in pod axes (X right, Y up, Z toward rider, glass front ~Z=0), rotated to Fusion Z-up at the end:
# Fusion X right, Y forward, Z up, screen faces -Y.
import cadquery as cq, math, sys
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
RT=0.0                                   # v3r: all corners the same again
def rr2(w,h,r,rt): return rr(w,h,r)
def slab(sk,z0,z1,cx=0,cy=0): return cq.Workplane("XY").workplane(offset=z0).center(cx,cy).placeSketch(sk).extrude(z1-z0)
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
GW,GH,GR,GT=92.44,61.00,6.0,1.10        # cover glass (Waveshare drawing)
CLR,GLUE=0.2,0.3                         # glass edge gap, glue bed
WALL=2.5
OW,OH=105.2,GH+2*CLR+2*WALL              # wider for the 99 mm Fowecry MOSFET board
OR=GR+CLR+WALL
ZS=-15.0                                 # front/back split
ZB=-37.8                                 # v3r: back face 4.3 deeper for the REAL MOSFET board (terminals 14.1 above PCB)
PF=-19.0                                 # MOSFET PCB front face (toward the screen)
PB=PF-1.5                                # MOSFET PCB component face (Joel's model: 1.5 thick)
EXT=27.0                                 # v3r: pod widened on the RIGHT for a side bulkhead plug; screen stays at X=0
EC=EXT/2
PD=GT+GLUE                               # glass pocket depth
# LCD module footprint behind the glass, pod axes (board y -> -X, board x -> Y)
LX0,LX1,LY=-38.92,43.92,27.28
# ---------------- FRONT RING ----------------
front=slab(rr2(OW+EXT,OH,OR,RT),ZS,0,cx=EC).faces(">Z").edges().fillet(1.2)
front=front.cut(slab(rr(GW+2*CLR,GH+2*CLR,GR+CLR),-PD,0.5))                 # glass pocket
front=front.cut(box(LX0-0.6,LX1+1.2,-LY-0.5,LY+0.5,-3.2,-PD+0.01))           # opening through the ledge
front=front.cut(slab(rr2(OW+EXT-2*WALL-0.6,OH-2*WALL-0.6,OR-WALL,RT-WALL-0.3),ZS-1,-3.2,cx=EC))      # cavity behind ledge (wall ~2.8)
AX,AY=46.7,26.8                                                              # corner anchor posts for the board arms
for sx in (-1,1):
    for sy in (-1,1):
        front=front.union(cq.Workplane("XY").workplane(offset=ZS).center(sx*AX,sy*AY).circle(3.6).extrude(ZS*-1-8.6))
MX,MY=45.5,22.0                                                              # MOSFET board holes (91 x 44, from Joel's STEP)
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
TP=1.5                                   # v3r: back cover's ENDS taper in 1.5 mm toward the back (~4.6 deg) so it reads slimmer
def taper(w,h,r,z0,z1,t):                # loft: full outline at z1 (split) -> ends pulled in by t at z0 (back). Ends only, so top/bottom walls keep the antenna pocket
    a=cq.Workplane("XY").workplane(offset=z0).center(EC,0).placeSketch(rr(w-2*t,h,r)).extrude(0.01).faces('<Z').wires().val()
    b=cq.Workplane("XY").workplane(offset=z1).center(EC,0).placeSketch(rr(w,h,r)).extrude(-0.01).faces('>Z').wires().val()
    return cq.Workplane("XY").add(cq.Solid.makeLoft([a,b],True))
back=taper(OW+EXT,OH,OR,ZB,ZS,TP)
try: back=back.faces("<Z").edges().fillet(6)
except Exception as e: print('back fillet skip',e)
back=back.cut(taper(OW+EXT-2*WALL,OH-2*WALL,OR-WALL,ZB+2.5,ZS+0.1,TP*(ZS-ZB-2.5)/(ZS-ZB)))
for x,y in CB:   # MOSFET board standoffs, M3 heat-set in the top, board screwed down with M3x6 from inside
    back=back.union(cq.Workplane("XY").workplane(offset=ZB+1).center(x,y).circle(3.6).extrude(PB-ZB-1))
    back=back.cut(cq.Workplane("XY").workplane(offset=PB-5.6).center(x,y).circle(2.0).extrude(5.7))
for x,y in CK:   # pod closure tubes, M3x25 from the back
    back=back.union(cq.Workplane("XY").workplane(offset=ZB+1).center(x,y).circle(3.4).extrude(ZS-ZB-1.3))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(1.7).extrude(40))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(3.1).extrude(5.5))    # M3 head counterbore
back=back.cut(box(-49.9,49.9,-26.4,26.4,-21.0,ZS+1))        # clear the MOSFET PCB and plug zone
back=back.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZS-1.0,ZS+0.1))  # keep tube tops below the seal face
# v3r: GPS receiver sticks straight onto the back wall (no pad)
# GPS ceramic antenna pocket in the top wall: wall thinned to 1.6 mm over the antenna
# (size ESTIMATED from Joel's listing photos, scaled off the 12 x 15 board: ~19 x 6 x 5)
back=back.cut(box(51,71,OH/2-WALL-0.01,OH/2-1.6,-30.0,-21.0))   # v3r: moved over the WS28 end, clear of the 14 mm terminals
# TPU seal groove on the back cover's front face
back=back.cut(slab(rr2(OW+EXT-1.6,OH-1.6,OR-0.8,RT-0.8),ZS-1.2,ZS+0.1,cx=EC).cut(slab(rr2(OW+EXT-4.0,OH-4.0,OR-2.0,RT-2.0),ZS-2,ZS+1,cx=EC)))
# fingers that press the board plug home (from the bottom wall)
# (no plug fingers: the MOSFET board's PCB sits 0.5 mm behind the plug and holds it in)
# exit boot and breather vent on the bottom face
by=-OH/2
# v3r: cable boot gone (everything goes through the plug). Breather is now a flush 3 mm hole
# with a 12 mm adhesive PTFE vent stuck over it inside (no lump on the outside).
back=back.cut(cq.Workplane("XZ").workplane(offset=-by+4).center(24,-27).circle(1.5).extrude(8))
# mounting bosses on the back (M5 heat-set, 60 c-c like v1/v2)
for x in (-30,30):
    back=back.union(cq.Workplane("XY").add(cq.Solid.makeCone(5.5,8.0,7.0,cq.Vector(x,0,ZB-7))).union(cq.Workplane("XY").workplane(offset=ZB-0.5).center(x,0).circle(8).extrude(1.5)))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-7.5).center(x,0).circle(3.2).extrude(9))
# ---- v3r: FLYLEAD out of the back through an M20 x 1.5 cable gland, straight into the nav tower ----
# Joel 2026-11-24: AMPSEAL too big -> one sheathed ~10 mm cable (17 cores) through a sealed gland.
# The gland screws into a printed M20 x 1.5 thread in a boss on the back (no locknut inside,
# so nothing clashes with the boards). Gland size is a TYPICAL nylon IP68 M20 (6-12 mm cable): hex 24 AF.
# v3r (Joel 2026-11-25: WS28 'looks ridiculous', picked TWO SMALL M12 ROUND PLUGS).
# Two front-mount M12 panel sockets stacked on the back face in the right-hand extension.
# Sizes are TYPICAL M12 panel-socket values, not a chosen part: M16 x 1.5 panel thread (hole 16.2),
# ~20 mm hex/flange outside, ~8 mm stick-out, ~13 mm body + 15 mm solder-cup tails inside.
# Plug shown is a typical straight moulded cordset (~20 mm coupling ring, ~45 mm long). A right-angle
# cordset would turn the cable down and stick out ~30 mm less.
MXP=61.0                                  # hex kept on the flat part of the back face
M12Y=(13.5,-13.5)                         # top: 8-pin (outputs), bottom: 12-pin (power + signals)
m12s=None; m12p=None
for y in M12Y:
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(MXP,y).circle(16.2/2).extrude(WALL+2))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-0.6).center(MXP,y).polygon(6,23.1).extrude(0.6))   # 0.6 mm seat for the O-ring flange
    sk=(cq.Workplane("XY").workplane(offset=ZB-8).center(MXP,y).circle(6.0).extrude(8-0.6)                 # M12 male thread stub
        .union(cq.Workplane("XY").workplane(offset=ZB-0.6-2.0).center(MXP,y).polygon(6,23.1).extrude(2.0))      # flange/hex
        .union(cq.Workplane("XY").workplane(offset=ZB).center(MXP,y).circle(7.9).extrude(WALL+0.01))            # through the wall
        .union(cq.Workplane("XY").workplane(offset=ZB+WALL).center(MXP,y).polygon(6,23.1).extrude(3.0))         # inside nut
        .union(cq.Workplane("XY").workplane(offset=ZB+WALL+3).center(MXP,y).circle(6.5).extrude(12.0)))         # body + solder cups
    pl=(cq.Workplane("XY").workplane(offset=ZB-8-0.2-14).center(MXP,y).circle(10.0).extrude(14)                  # knurled coupling ring
        .union(cq.Workplane("XY").workplane(offset=ZB-8-45).center(MXP,y).circle(7.5).extrude(31))
        .union(cq.Workplane("XY").workplane(offset=ZB-8-75).center(MXP,y).circle(3.5).extrude(30)))
    m12s=sk if m12s is None else m12s.union(sk)
    m12p=pl if m12p is None else m12p.union(pl)
# ---- v3r POLISH PASS ----
# 2) shadow-line reveal at the split: 0.8 tall x 0.6 deep groove round the front ring's back edge
rev=slab(rr2(OW+EXT+4,OH+4,OR+2,RT+2),ZS-0.01,ZS+0.8,cx=EC).cut(slab(rr2(OW+EXT-1.2,OH-1.2,OR-0.6,max(RT-0.6,0.4)),ZS-1,ZS+2,cx=EC))
front=front.cut(rev)
# 3) soften the glass pocket rim
try: front=front.faces(">Z").edges(cq.selectors.BoxSelector((-GW/2-1,-GH/2-1,-0.5),(GW/2+1,GH/2+1,0.5))).chamfer(0.5)
except Exception as e: print('pocket chamfer skip',e)
# 4) maker's mark debossed on the back, 0.4 deep
try:
    mark=cq.Workplane("XY").workplane(offset=ZB-0.01).center(EC,-24).text("XL125R  DASH",4.2,0.4,kind="bold",halign="center",valign="center")
    back=back.cut(mark.mirror("YZ",basePointVector=(EC,0,0)))
except Exception as e: print('mark skip',e)
# ---------------- PARTS INSIDE ----------------
seal=slab(rr2(OW+EXT-1.8,OH-1.8,OR-0.9,RT-0.9),ZS-1.0,ZS+0.4,cx=EC).cut(slab(rr2(OW+EXT-3.8,OH-3.8,OR-1.9,RT-1.9),ZS-2,ZS+1,cx=EC))
board=cq.importers.importStep(SCR+'ws/wsrepo/hardware/mechanical/ESP32-S3-Touch-LCD-3_5.stp')
board=board.rotate((0,0,0),(0,0,1),90).translate((0,0,-PD))
# v3r: Joel's own STEP of the Fowecry board (board Y = up from PCB underside, Z = across).
# Rotate so its components face the back (-Z) and its Z axis runs up the pod. Which terminal strip
# ends up at the top is MY CHOICE (unconfirmed): 16 mm output strip at the top, 11 mm input strip + VIN at the bottom.
mos=cq.importers.importStep(SCR+'mos/mosfet.step').rotate((0,0,0),(1,0,0),-90).translate((0,0,PF))
parts={
 'lipo_500_30x36x5':    box(-40,-4,-15,15,PF-10.6-5.0,PF-10.6),   # v3r: smaller cell lying on the jumper headers (tops 10.5 mm, Joel's model)
 'gps_receiver_atgm336h': box(33,45,-7.5,7.5,ZB+2.5,ZB+2.5+5.0),
 'gps_ceramic_antenna_est': box(52,70,OH/2-WALL-5.0+0.9,OH/2-1.6,-28.5,-22.5),
 'mosfet_fowecry_99x52':mos,
 'board_screws_m3x6':  cq.Workplane().add([cq.Workplane('XY').workplane(offset=PF).center(x,y).circle(2.75).extrude(2.0).val() for x,y in CB]),
 'm12_sockets_x2': m12s,
 'm12_plugs_x2_straight': m12p,
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
asm=cq.Assembly(name="xl-dash-pod-v3r")
asm.add(rot(front),name="front_ring",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(back),name="back_cover",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(seal),name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
asm.add(rot(board),name="waveshare_s3_lcd35",color=cq.Color(0.1,0.35,0.2))
cols={'gps_receiver_atgm336h':(0.2,0.45,0.25),'gps_ceramic_antenna_est':(0.75,0.55,0.4),'gps_bn220':(0.2,0.2,0.22),'lipo_500_30x36x5':(0.75,0.75,0.8),'mcp23017_guess':(0.1,0.3,0.7),'gps_bn220':(0.2,0.2,0.22),'buck_pololu':(0.1,0.5,0.2),'mosfet_fowecry_99x52':(0.15,0.25,0.6),'board_plug':(0.05,0.05,0.05),'board_screws_m3x6':(0.7,0.7,0.7),'m12_sockets_x2':(0.75,0.76,0.78),'m12_plugs_x2_straight':(0.12,0.12,0.13),}
for n,p in parts.items(): asm.add(rot(p),name=n,color=cq.Color(*cols[n]))
OUT=SCR+'cad3/out18/'
import os; os.makedirs(OUT,exist_ok=True)
asm.save(OUT+'xl-dash-pod-v3r-assembly.step')
for n,w in (('front',front),('back',back),('seal',seal)):
    cq.exporters.export(rot(w),OUT+f'xl-dash-pod-v3r-{n}.step')
    cq.exporters.export(rot(w),OUT+f'xl-dash-pod-v3r-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(rot(w),OUT+f'part-{n}.stl')
cq.exporters.export(rot(board),OUT+'part-board.stl',tolerance=0.1,angularTolerance=0.3)
bb=rot(shell).val().BoundingBox();print('pod bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f'%(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax))
