# v8 (2026-11-25, Joel picked RS 250-0742 male + 250-0736 female, pre-wired, M16x1.5): v7 with the RS front-mount
# male socket (flange outside, nut inside, see rsm12.py; sizes guessed).
# v7 (2026-11-25, Joel: 'shrink the length slightly and make the screen central'): screen centred, 3.5 mm extra each side
# (104.8 wide). Socket tucked behind the board's thin right edge (board only 4.5 deep for x>40, from its STEP), centre z -14.5,
# so its leads run straight in under the board parts. LiPo moved left to x 4..40.
# v6 (2026-11-25, Joel: 'make the cable come out the side, lose the visor for now'): v4 side-plug layout with Joel's
# Hamadap M12 12-pin back-mount socket (M16 panel thread; hex/nut/length split ESTIMATED from his photo) in the RIGHT side wall.
# No visor. Parts layout as v4c.
# XL dash v4 SPLIT: SCREEN POD only (Joel 2026-11-25: "screen can be a lovely lightweight thing with a small
# plug on one side and the brain can go under the tank"). Waveshare ESP32-S3-Touch-LCD-3.5 + 500 mAh LiPo + GPS.
# MOSFET board, AMPSEAL and PCA9685 live in the separate brain box.
# Link to the box: ONE 8-pin M12 A-coded socket on the RIGHT side face (Joel: 'M14' read as M12) carrying
# 5V, GND, SDA, SCL, RPM, brake + 2 spare. M12 socket/plug sizes are TYPICAL values (as v3r), not a chosen part.
# Slim rectangle: deep front ring (holds everything) + flat 2.5 mm back lid.
# Pod axes: X right, Y up, Z toward rider (glass front ~Z=0); rotated to Fusion Z-up at export (screen faces -Y).
import cadquery as cq, math, sys
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
def slab(sk,z0,z1,cx=0,cy=0): return cq.Workplane("XY").workplane(offset=z0).center(cx,cy).placeSketch(sk).extrude(z1-z0)
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
GW,GH,GR,GT=92.44,61.00,6.0,1.10        # cover glass (Waveshare drawing)
CLR,GLUE=0.2,0.3
WALL=2.5
OW,OH=GW+2*CLR+2*WALL,GH+2*CLR+2*WALL    # 97.84 x 66.4 (screen only)
EXT=7.0; EC=0.0                       # extra width on the RIGHT for the M8 socket + GPS antenna
OR=GR+CLR+WALL
ZS=-24.0                                 # split: front ring is the body, back is a flat lid
ZB=-26.5                                 # back face; M12 inside nut (20 AF) sets the depth
PD=GT+GLUE
LX0,LX1,LY=-38.92,43.92,27.28
XR=OW/2+EXT/2                              # right outer face x
# ---------------- FRONT RING ----------------
front=slab(rr(OW+EXT,OH,OR),ZS,0,cx=EC).faces(">Z").edges().fillet(1.2)
front=front.cut(slab(rr(GW+2*CLR,GH+2*CLR,GR+CLR),-PD,0.5))
front=front.cut(box(LX0-0.6,LX1+1.2,-LY-0.5,LY+0.5,-3.2,-PD+0.01))
front=front.cut(slab(rr(OW+EXT-2*WALL-0.6,OH-2*WALL-0.6,OR-WALL),ZS-1,-3.2,cx=EC))
CB=[(-43.4,-27.3),(-43.4,27.3),(43.4,27.3),(43.4,-27.3)]
for x,y in CB:
    front=front.union(cq.Workplane("XY").workplane(offset=ZS).center(x,y).circle(3.6).extrude(ZS*-1-8.6))
    front=front.cut(cq.Workplane("XY").workplane(offset=ZS-0.1).center(x,y).circle(2.0).extrude(6.1))
HX,HY=36.0,24.25
PCBZ=-6.4-PD
for sx in (-1,1):
    for sy in (-1,1):
        arm=(cq.Workplane("XY").workplane(offset=PCBZ-2.2).moveTo(sx*HX,sy*HY).circle(2.1).extrude(2.2)
             .union(cq.Workplane("XY").workplane(offset=PCBZ-2.2).polyline([(sx*(HX+0.6),sy*(HY-1.8)),(sx*43.4,sy*(27.3-2.6)),(sx*43.4,sy*27.3),(sx*(HX+1),sy*(HY+2.4))]).close().extrude(2.2)))
        front=front.union(arm)
        front=front.union(cq.Workplane("XY").workplane(offset=PCBZ).center(sx*HX,sy*HY).circle(0.85).extrude(1.4))
# shadow-line reveal at the split + soft glass rim (as v3o)
rev=slab(rr(OW+EXT+4,OH+4,OR+2),ZS-0.01,ZS+0.8,cx=EC).cut(slab(rr(OW+EXT-1.2,OH-1.2,OR-0.6),ZS-1,ZS+2,cx=EC))
front=front.cut(rev)
try: front=front.faces(">Z").edges(cq.selectors.BoxSelector((-GW/2-1,-GH/2-1,-0.5),(GW/2+1,GH/2+1,0.5))).chamfer(0.5)
except Exception as e: print('pocket chamfer skip',e)
# ---- M12 8-pin socket in the RIGHT side face, all in the front ring (centre z -13.6, y -14) ----
SY,SZ=-13.0,-14.5
ax=lambda x0,L,r: cq.Workplane("YZ").workplane(offset=x0).center(SY,SZ).circle(r).extrude(L)
hexw=lambda x0,L,af: cq.Workplane("YZ").workplane(offset=x0).center(SY,SZ).polygon(6,af/math.cos(math.pi/6)).extrude(L)
front=front.cut(ax(XR-WALL-1,WALL+2,8.1))                 # 16.2 hole for the M16 panel thread
import sys as _s; _s.path.insert(0,'/home/user/chassis-bench/files/dash-split/src'); import rsm12
sock=rsm12.socket(lambda u,L,r: ax(XR+u,L,r), lambda u,L,af: hexw(XR+u,L,af), WALL+0.3,leads=False)   # RS 250-0742 male, front mount
# its pre-wired lead (shielded, ~6 mm sheath GUESSED) leaves the potted end and S-bends down under the board's deep zone
_x0=XR-rsm12.THR_L
_path=cq.Workplane("XY").spline([(_x0,SY,SZ),(_x0-7,SY,SZ-3.0),(_x0-16,SY,SZ-4.5)],tangents=[(-1,0,0),(-1,0,0)])
lead=cq.Workplane("YZ").workplane(offset=_x0).center(SY,SZ).circle(3.0).sweep(_path)
sock=sock.union(lead)
def _elbow(uc):   # elbow body r8 dropping DOWN from the nut, then the 6.4 mm cable (RS 877-1208, sizes guessed)
    x=XR+uc
    body=cq.Workplane("XZ").workplane(offset=-(SY+8)).center(x,SZ).circle(8.5).extrude(26)    # y SY+8 .. SY-18
    cab=cq.Workplane("XZ").workplane(offset=-(SY-18)).center(x,SZ).circle(3.2).extrude(40)
    return body.union(cab)
plug=rsm12.plug_ra(lambda u,L,r: ax(XR+u,L,r),_elbow)                                    # RS 877-1208 right-angle female end
# ---------------- BACK COVER ----------------
back=slab(rr(OW+EXT,OH,OR),ZB,ZS,cx=EC)
try: back=back.faces("<Z").edges().fillet(1.5)
except Exception as e: print('back fillet skip',e)
for x,y in CB:
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(1.7).extrude(40))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(3.1).extrude(1.2))
front=front.cut(slab(rr(OW+EXT-1.6,OH-1.6,OR-0.8),ZS-0.1,ZS+1.2,cx=EC).cut(slab(rr(OW+EXT-4.0,OH-4.0,OR-2.0),ZS-2,ZS+2,cx=EC)))   # seal groove in the ring's back face
# breather: flush 3 mm hole in the bottom, adhesive PTFE vent inside
front=front.cut(cq.Workplane("XZ").workplane(offset=OH/2-4).center(-20,-18.0).circle(1.5).extrude(8))
# mounting bosses (M5 heat-set, 60 c-c as before)
for x in (-30,30):
    back=back.union(cq.Workplane("XY").add(cq.Solid.makeCone(5.5,8.0,7.0,cq.Vector(x,0,ZB-7))).union(cq.Workplane("XY").workplane(offset=ZB-0.5).center(x,0).circle(8).extrude(1.5)))
    back=back.cut(cq.Workplane("XY").workplane(offset=ZB-7.5).center(x,0).circle(3.2).extrude(9))
try:
    mark=cq.Workplane("XY").workplane(offset=ZB-0.01).center(EC,-24).text("XL125R  DASH",4.2,0.4,kind="bold",halign="center",valign="center")
    back=back.cut(mark.mirror("YZ",basePointVector=(EC,0,0)))
except Exception as e: print('mark skip',e)
# ---------------- PARTS INSIDE ----------------
seal=slab(rr(OW+EXT-1.8,OH-1.8,OR-0.9),ZS-0.4,ZS+1.0,cx=EC).cut(slab(rr(OW+EXT-3.8,OH-3.8,OR-1.9),ZS-2,ZS+2,cx=EC))
parts={
 'lipo_500_30x36x5':        box(4,40,-8,22,-23.8,-18.8),
 'gps_receiver_atgm336h':   box(-44,-31,6,21.7,-23.8,-20.3),
 'gps_ceramic_antenna_est': box(-21,-2,21,27,-23.5,-18.5),
 'board_plug':              box(-20.6,20.6,-26.3,-19.7,-15.5,-12.95).union(box(-20.6,20.6,-19.7,-12.3,-18.2,-13.0)),
 'm12_socket_8pin':          sock,
 'm12_plug_straight':        plug,
}
# ---------------- CHECKS ----------------
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
shell=front.union(back)
print('front valid',front.val().isValid(),'back valid',back.val().isValid())
for n,p in parts.items():
    print('%-24s shell %.1f'%(n,vol(shell,p)))
    if vol(shell,p)>0.5:
        for so in shell.intersect(p).solids().vals():
            b=so.BoundingBox(); print('     at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f v %.1f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax,so.Volume()))
    for m,q in parts.items():
        if m>n:
            v=vol(p,q)
            if v>0.01: print('   clash',n,m,round(v,1))
# board keep-out: Waveshare PCB + its back-side parts occupy z -PD..-13.7 over roughly x -46..46, y -30.5..30.5 (from its STEP)
bko=box(-46,40,-30.5,30.5,-13.7,-PD).union(box(40,46,-30.5,30.5,-PD-4.5,-PD))   # deep only for x<40 (STEP)
for n,p in parts.items(): print('%-24s vs board zone %.1f'%(n,vol(bko,p)))
# ---------------- EXPORT ----------------
rot=lambda w: w.rotate((0,0,0),(1,0,0),90)
OUT=SCR+'cad4/out8/'
import os; os.makedirs(OUT,exist_ok=True)
asm=cq.Assembly(name="xl-dash-screen-pod-v8")
asm.add(rot(front),name="front_ring",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(back),name="back_cover",color=cq.Color(0.13,0.15,0.17))
asm.add(rot(seal),name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
cols={'lipo_500_30x36x5':(0.75,0.75,0.8),'gps_receiver_atgm336h':(0.2,0.45,0.25),'gps_ceramic_antenna_est':(0.75,0.55,0.4),'board_plug':(0.05,0.05,0.05),'m12_socket_8pin':(0.75,0.76,0.78),'m12_plug_straight':(0.12,0.12,0.13)}
for n,p in parts.items(): asm.add(rot(p),name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-dash-screen-pod-v8-assembly-no-board.step')
for n,w in (('front',front),('back',back),('seal',seal)):
    cq.exporters.export(rot(w),OUT+f'xl-dash-screen-pod-v8-{n}.step')
    cq.exporters.export(rot(w),OUT+f'xl-dash-screen-pod-v8-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(rot(w),OUT+f'part-{n}.stl')
bb=rot(shell).val().BoundingBox();print('pod bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f'%(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax))
print('mass est (PETG 1.27 g/cc, solid):',round(shell.val().Volume()*1.27/1000,1),'g')
# The lead's first ~6 mm dips into the crude -13.7 board zone, but in the Waveshare STEP nothing over x>30,
# y -17..-9 sits deeper than z -9.4, so the real gap is ~2 mm (checked 2026-11-25).
