# XL dash DOCK IDEA v2 (Joel: strong magnets + locating pins, no latch; standard pogo strips): removable HEAD (Waveshare ESP32-S3 3.5" + LiPo) on a latched DOCK
# (MOSFET board, GPS, 5 V buck, loom) through 18 pogo pins.
# Pod axes while building: X right, Y up, Z toward the rider, glass front face at Z=0.
# Exported rotated to Fusion Z-up like the v3 pod: X right, Y forward, Z up, screen faces -Y.
import cadquery as cq, math, os, sys
OUT=sys.argv[1] if len(sys.argv)>1 else 'out/'
os.makedirs(OUT,exist_ok=True)
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
def slab(sk,z0,z1,cx=0,cy=0): return cq.Workplane("XY").workplane(offset=z0).center(cx,cy).placeSketch(sk).extrude(z1-z0)
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cyl(x,y,z0,z1,r): return cq.Workplane("XY").workplane(offset=z0).center(x,y).circle(r).extrude(z1-z0)
def tryf(f,w,msg):
    try: return f(w)
    except Exception as e: print('skip',msg,e); return w
GW,GH,GR,GT=92.44,61.00,6.0,1.10        # cover glass (Waveshare drawing)
CLR,GLUE=0.2,0.3
WALL=2.5
OW,OH=105.2,GH+2*CLR+2*WALL             # 105.2 x 66.4: same footprint as v3j, so head and dock line up
OR=GR+CLR+WALL                          # R8.7
PD=GT+GLUE
LX0,LX1,LY=-38.92,43.92,27.28           # LCD module behind the glass
# ================= HEAD =================
ZS=-14.0       # head split: front ring / head back
ZH=-17.5       # head back face = mating face (head is 17.5 deep)
SKIN=1.8
PADY=(-24.27,-21.73)   # v2: pogo lands straight on J8 (2 x 16 @ 2.54, female) via a long-pin header
PADS=[((i-7.5)*2.54,y) for y in PADY for i in range(16)]
front=slab(rr(OW,OH,OR),ZS,0).faces(">Z").edges().fillet(1.2)
front=front.cut(slab(rr(GW+2*CLR,GH+2*CLR,GR+CLR),-PD,0.5))
front=front.cut(box(LX0-0.6,LX1+1.2,-LY-0.5,LY+0.5,-3.2,-PD+0.01))
front=front.cut(slab(rr(OW-2*WALL-0.6,OH-2*WALL-0.6,OR-WALL),ZS-1,-3.2))
AX,AY=46.7,26.8
KX,KY=46.7,28.6
CK=[(sx*KX,sy*KY) for sx in (-1,1) for sy in (-1,1)]
for sx in (-1,1):
    for sy in (-1,1):
        front=front.union(cyl(sx*AX,sy*AY,ZS,-8.6,3.6))
for x,y in CK:
    front=front.union(cyl(x,y,ZS,-8.6,3.6))
    front=front.cut(cyl(x,y,ZS-0.1,ZS+5.0,2.0))          # M3 heat-set (5 deep)
HX,HY=36.0,24.25
PCBZ=-6.4-PD
for sx in (-1,1):
    for sy in (-1,1):
        arm=(cq.Workplane("XY").workplane(offset=PCBZ-2.2).moveTo(sx*HX,sy*HY).circle(2.1).extrude(2.2)
             .union(cq.Workplane("XY").workplane(offset=PCBZ-2.2).polyline([(sx*(HX+0.6),sy*(HY-1.8)),(sx*AX,sy*(AY-2.6)),(sx*AX,sy*AY),(sx*(HX+1),sy*(HY+2.4))]).close().extrude(2.2)))
        front=front.union(arm).union(cyl(sx*HX,sy*HY,PCBZ,PCBZ+1.4,0.85))
# shadow-line reveal at the head split
front=front.cut(slab(rr(OW+4,OH+4,OR+2),ZS-0.01,ZS+0.8).cut(slab(rr(OW-1.2,OH-1.2,OR-0.6),ZS-1,ZS+2)))
front=tryf(lambda w:w.faces(">Z").edges(cq.selectors.BoxSelector((-GW/2-1,-GH/2-1,-0.5),(GW/2+1,GH/2+1,0.5))).chamfer(0.5),front,'glass rim chamfer')

# head back: thin shell, mating face, pad window, hooks and latch tongue
hb=slab(rr(OW,OH,OR),ZH,ZS)
hb=tryf(lambda w:w.faces("<Z").edges().chamfer(0.6),hb,'head back chamfer')
hb=hb.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZH+SKIN,ZS+0.1))
for x,y in CK:   # closure tubes, M3 x 10 from the mating face (heads hidden when docked)
    hb=hb.union(cyl(x,y,ZH+0.5,ZS-0.3,3.4))
    hb=hb.cut(cyl(x,y,ZH-1,ZS+1,1.7)).cut(cyl(x,y,ZH-1,ZH+2.0,3.1))
# seal groove on the head back's front face
hb=hb.cut(slab(rr(OW-1.6,OH-1.6,OR-0.8),ZS-1.2,ZS+0.1).cut(slab(rr(OW-4.0,OH-4.0,OR-2.0),ZS-2,ZS+1)))
# adapter board window (board sits flush in it, edge glued/potted)
AW0,AW1,AH0,AH1=-24.0,24.0,-27.5,-18.5
# v2: pin-guide block behind J8: the long-pin header's ends come through 32 holes flush with the back face
hb=hb.union(box(-21.8,21.8,-26.6,-19.4,ZH+0.5,-15.6))
for x,y in PADS: hb=hb.cut(box(x-0.42,x+0.42,y-0.42,y+0.42,ZH-1,-15.5))
# (v1 hook/tongue helpers kept for reference, not used in v2)
# bottom hook tongues (hook-and-tilt): lip points down, catches behind the dock front wall
HKX=31.0
def hook(sx):
    b=box(sx*HKX-6,sx*HKX+6,-26.4,-22.4,ZH-5.7,ZH+0.5)
    lip=box(sx*HKX-6,sx*HKX+6,-28.4,-26.0,ZH-5.7,ZH-3.5)
    h=b.union(lip)
    return tryf(lambda w:w.edges("|Z").fillet(1.2),h,'hook fillet')
# top latch tongue with a barb on its right side (the dock's sliding bar snaps over it)
def tongue(zf):
    t=box(-8,6,20.5,24.5,zf-5.3,zf+0.5)                     # neck
    barb=(cq.Workplane("XZ").polyline([(6,zf-5.2),(8,zf-5.2),(6,zf-6.7)]).close().extrude(-4).translate((0,20.5,0)))
    tip=box(-8,6,20.5,24.5,zf-6.7,zf-5.2)
    t=t.union(barb).union(tip)
    return tryf(lambda w:w.edges("|Y").fillet(0.4),t,'tongue fillet')
# --- v2: 4 magnet pockets + 2 locating-pin holes in the head back ---
MAG=[(-40,-16),(40,-16),(-18,24.3),(18,24.3)]     # 12 x 3 N52 discs
MR,MT,MSK=6.1,3.0,0.5                            # pocket radius, magnet thickness, skin over the magnet
PIN=[(-42,10),(42,10)]                           # 4 mm stainless dowels (h6), stand 4.5 proud of the dock
for x,y in MAG:
    hb=hb.union(cyl(x,y,ZH+0.5,ZS-0.3,7.5)).cut(cyl(x,y,ZH+MSK,ZH+MSK+MT+0.05,MR))
for x,y in PIN:
    hb=hb.union(cyl(x,y,ZH+0.5,ZH+6.0,4.2))
    hb=hb.cut(cyl(x,y,ZH-1,ZH+5.2,2.06))
    hb=tryf(lambda w:w.faces("<Z").edges(cq.selectors.BoxSelector((x-2.6,y-2.6,ZH-0.2),(x+2.6,y+2.6,ZH+0.2))).chamfer(0.5),hb,'pin hole chamfer')
# flush breather (3 mm, PTFE vent inside) and maker's mark
hb=hb.cut(cq.Workplane("XZ").workplane(offset=OH/2-4).center(-24,-15.8).circle(1.5).extrude(8))
try:
    mk=cq.Workplane("XY").workplane(offset=ZH-0.01).center(0,6).text("XL125R  DASH",4.2,0.4,kind="bold",halign="center",valign="center")
    hb=hb.cut(mk.mirror("YZ"))
except Exception as e: print('mark skip',e)
hseal=slab(rr(OW-1.8,OH-1.8,OR-0.9),ZS-1.0,ZS+0.4).cut(slab(rr(OW-3.8,OH-3.8,OR-1.9),ZS-2,ZS+1))

# head internals
gl=slab(rr(GW,GH,GR),-PD,-PD+GT)
ws=(box(LX0,LX1,-LY,LY,-PD-6.0,-PD-0.55).union(box(-39,39,-27.27,27.27,-PD-6.4,-PD-4.8))
    .union(box(-20.6,20.6,-25.6,-20.4,-PD-11.5,-PD-6.4)).union(box(32.4,40,-4.5,4.5,-PD-9.65,-PD-5.6)))
lipo=box(-31,31,-17.5,17.5,-14.4,-9.4)
# pogo ADAPTER board: 2x16 header (mates J8), 48 x 9 PCB, 18 gold pads (2 x 9 @ 2.54) on the mating face
# long-pin 2 x 16 header pushed into J8 (GOLD plated, pins trimmed flush with the back face)
lph=box(-20.32,20.32,-25.54,-20.46,-15.4,-12.9)
lpp=cq.Workplane().add([box(x-0.32,x+0.32,y-0.32,y+0.32,ZH+0.02,-7.9).val() for x,y in PADS])
# ================= DOCK =================
ZF=ZH-0.3         # dock mating face (0.3 gap; TPU ring + pogo pins close it)
FW=3.0            # dock front wall
ZDS=-34.0         # dock split: tub / back cover
ZDB=-40.5         # dock back face
dk=slab(rr(OW,OH,OR),ZDS,ZF)
dk=dk.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZDS-0.1,ZF-FW))
# shadow-line reveal at the head/dock join and at the dock split
dk=dk.cut(slab(rr(OW+4,OH+4,OR+2),ZF-0.8,ZF+0.01).cut(slab(rr(OW-1.2,OH-1.2,OR-0.6),ZF-2,ZF+1)))
dk=dk.cut(slab(rr(OW+4,OH+4,OR+2),ZDS-0.01,ZDS+0.8).cut(slab(rr(OW-1.2,OH-1.2,OR-0.6),ZDS-1,ZDS+2)))
DK=[(sx*45.5,sy*28.9) for sx in (-1,1) for sy in (-1,1)]
for x,y in DK:
    dk=dk.union(cyl(x,y,ZDS,ZF-FW+0.1,2.8)).cut(cyl(x,y,ZDS-0.1,ZDS+5.0,2.0))
# MOSFET board standoffs (board components face the back: terminals reachable with the back cover off)
MX,MY=45.0,21.5
CB=[(sx*MX,sy*MY) for sx in (-1,1) for sy in (-1,1)]
MZ0=ZF-FW-3.6     # board front face
for x,y in CB:
    dk=dk.union(cyl(x,y,MZ0,ZF-FW+0.1,3.2)).cut(cyl(x,y,MZ0-0.1,MZ0+3.5,1.6))
# hook slots (bottom) and latch-tongue slot (top)
# v2: magnet pockets (from inside, 0.5 skin), locating dowels pressed into bosses, pogo strip slots
for x,y in MAG:
    dk=dk.union(cyl(x,y,ZF-MSK-MT-0.8,ZF-FW+0.1,7.5)).cut(cyl(x,y,ZF-MSK-MT-0.05,ZF-MSK,MR))
for x,y in PIN:
    dk=dk.union(cyl(x,y,ZF-FW-2.5,ZF-FW+0.1,4.5)).cut(cyl(x,y,ZF-FW-2.6,ZF+0.1,1.98))   # 3.96 press fit
dk=dk.cut(box(-21.05,21.05,-25.75,-20.25,ZF-FW-0.1,ZF+0.1))           # 2 x 16 pogo block sits flush in the wall
RING_O=slab(rr(50,14,5.0),ZF-1.0,ZF+0.1,cy=-23.0); RING_I=slab(rr(44,8,2.0),ZF-2,ZF+1,cy=-23.0)
dk=dk.cut(RING_O.cut(RING_I))
ring=slab(rr(49.6,13.6,4.8),ZF-1.0,ZH,cy=-23.0).cut(slab(rr(44.4,8.4,2.2),ZF-2,ZF+1,cy=-23.0))
# GPS ceramic antenna pocket in the top wall (wall thinned to 1.6, outside unchanged)
dk=dk.cut(box(13,34,OH/2-WALL-0.01,OH/2-1.6,-31.5,-23.0))
# flush breather in the bottom
dk=dk.cut(cq.Workplane("XZ").workplane(offset=OH/2-4).center(24,-28).circle(1.5).extrude(8))

# dock back cover
db=slab(rr(OW,OH,OR),ZDB,ZDS)
db=tryf(lambda w:w.faces("<Z").edges().fillet(5),db,'back fillet')
db=db.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZDB+2.5,ZDS+0.1))
for x,y in DK:
    db=db.union(cyl(x,y,ZDB+1,ZDS-0.3,2.6))
    db=db.cut(cyl(x,y,ZDB-1,ZDS+1,1.7)).cut(cyl(x,y,ZDB-1,ZDB+3.0,3.1))
db=db.cut(slab(rr(OW-1.6,OH-1.6,OR-0.8),ZDS-1.2,ZDS+0.1).cut(slab(rr(OW-4.0,OH-4.0,OR-2.0),ZDS-2,ZDS+1)))
# tapered M5 mounting bosses, 60 c-c (same as the v3 pod, so it fits the same tower bracket)
for x in (-30,30):
    db=db.union(cq.Workplane("XY").add(cq.Solid.makeCone(5.5,8.0,7.0,cq.Vector(x,0,ZDB-7))).union(cyl(x,0,ZDB-0.5,ZDB+1.0,8)))
    db=db.cut(cyl(x,0,ZDB-7.5,ZDB+1.5,3.2))
# loom exit: flush TPU grommet in a counterbore, centre of the back between the bosses
GRX,GRY=0.0,-10.0
db=db.cut(cyl(GRX,GRY,ZDB-0.1,ZDB+1.2,9.0)).cut(cyl(GRX,GRY,ZDB-1,ZDB+3,6.2))
db=db.union(cyl(GRX,GRY,ZDB+2.5,ZDB+4.5,7.5).cut(cyl(GRX,GRY,ZDB,ZDB+6,6.2)))   # inner collar
# GPS receiver pad and buck pad
db=db.union(box(8,21,2,17,ZDB+2.4,ZDB+3.5)).union(box(-25,-8,3,17,ZDB+2.4,ZDB+3.5))
try:
    mk=cq.Workplane("XY").workplane(offset=ZDB-0.01).center(0,-24).text("XL125R  DASH",4.2,0.4,kind="bold",halign="center",valign="center")
    db=db.cut(mk.mirror("YZ"))
except Exception as e: print('mark skip',e)
dseal=slab(rr(OW-1.8,OH-1.8,OR-0.9),ZDS-1.0,ZDS+0.4).cut(slab(rr(OW-3.8,OH-3.8,OR-1.9),ZDS-2,ZDS+1))

# dock internals
mos=box(-49.5,49.5,-26,26,MZ0-1.6,MZ0)
for x,y in CB: mos=mos.cut(cyl(x,y,MZ0-2,MZ0+1,1.6))
mos=(mos.union(box(-41,41,18,26,MZ0-11.6,MZ0-1.6)).union(box(-41,41,-26,-18,MZ0-11.6,MZ0-1.6))
        .union(box(-41,41,-17.8,17.8,MZ0-5.1,MZ0-1.6)))
pogo_pcb=box(-24,24,-28.5,-17.5,ZF-FW-1.6,ZF-FW)
pogo_body=box(-20.9,20.9,-25.6,-20.4,ZF-FW,ZF)   # standard 2 x 16, 2.54 mm pogo block (size GUESS), flush with the face
pogo=cq.Workplane().add([cyl(x,y,ZF-0.01,ZH-0.05,0.6).val() for x,y in PADS]+                # plungers ~1.0 compressed when docked (1.5 free)
                        [cyl(x,y,ZF-FW-0.2-1.6-2.5,ZF-FW-0.2,0.35).val() for x,y in PADS])  # tails through the carrier
mag_h=cq.Workplane().add([cyl(x,y,ZH+MSK,ZH+MSK+MT,6.0).val() for x,y in MAG])
mag_d=cq.Workplane().add([cyl(x,y,ZF-MSK-MT,ZF-MSK,6.0).val() for x,y in MAG])
magnets=cq.Workplane().add(mag_h.vals()+mag_d.vals())
dowels=cq.Workplane().add([cyl(x,y,ZF-FW-2.5,ZF+4.5,2.0).val() for x,y in PIN])
grx=box(9,21,2.5,16.5,ZDB+3.5,ZDB+6.5)
ant=box(14,33,26.4,31.4,-30.0,-24.0)
buck=box(-24,-9,3.5,16.5,ZDB+3.5,ZDB+8.0)
grommet=cyl(GRX,GRY,ZDB,ZDB+4.5,8.9).cut(cyl(GRX,GRY,ZDB-1,ZDB+6,5.0)).cut(cyl(GRX,GRY,ZDB+1.2,ZDB+4.6,9.0).cut(cyl(GRX,GRY,ZDB,ZDB+6,6.1)))
cable=cyl(GRX,GRY,ZDB-40,ZDB+8,5.0)

# ================= DOCK CAP (head off) =================
ZC=ZH+4.5
cap=slab(rr(OW,OH,OR),ZH,ZC).faces(">Z").edges().fillet(1.2)
cap=cap.cut(slab(rr(OW-2*WALL,OH-2*WALL,OR-WALL),ZH-0.1,ZC-1.6))
for x,y in MAG: cap=cap.union(cyl(x,y,ZH,ZC-1.5,7.5)).cut(cyl(x,y,ZH+MSK,ZH+MSK+MT+0.05,MR))
for x,y in PIN: cap=cap.union(cyl(x,y,ZH,ZC-1.5,4.2)).cut(cyl(x,y,ZH-1,ZH+2.9,2.06))
cap=cap.union(slab(rr(49,13.4,4.2),ZH,ZC-1.5,cy=-23.0))            # boss that presses the TPU ring
try:
    mk=cq.Workplane("XY").workplane(offset=ZC+0.01).center(0,0).text("XL125R",7,-0.4,kind="bold",halign="center",valign="center")
    cap=cap.cut(mk)
except Exception as e: print('cap mark skip',e)

# ================= CHECKS =================
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
head_shell=front.union(hb); dock_shell=dk.union(db)
parts={'lph':lph,'lpp':lpp,'pogo_body':pogo_body,'magnets':magnets,'ws':ws,'glass':gl,'lipo':lipo,'mos':mos,'pogo_pcb':pogo_pcb,'grx':grx,'ant':ant,'buck':buck,'grommet':grommet}
for n,a in (('front',front),('hb',hb),('dk',dk),('db',db),('cap',cap)): print(n,'valid',a.val().isValid())
for n,p in parts.items():
    print('%-9s head %.2f dock %.2f'%(n,vol(head_shell,p),vol(dock_shell,p)))
ks=list(parts)
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        v=vol(parts[ks[i]],parts[ks[j]])
        if v>0.01: print('  clash',ks[i],ks[j],round(v,2))
print('head vs dock',round(vol(head_shell,dock_shell),2),' pogo vs head',round(vol(pogo,head_shell),2),' pogo vs J8 pins',round(vol(pogo,lpp),2),' dowels vs head',round(vol(dowels,head_shell),2),' dowels vs dock',round(vol(dowels,dock_shell),2))

# ================= EXPORT =================
rot=lambda w: w.rotate((0,0,0),(1,0,0),90)
C=lambda *c: cq.Color(*c)
SH=(0.13,0.15,0.17)
items=[('head_front',front,SH),('head_back',hb,SH),('head_seal',hseal,(0.88,0.38,0.11)),('glass',gl,(0.02,0.02,0.03)),
 ('waveshare_simplified',ws,(0.1,0.35,0.2)),('lipo_1200',lipo,(0.75,0.75,0.8)),('longpin_header_body',lph,(0.05,0.05,0.05)),('longpin_header_pins',lpp,(0.85,0.65,0.2)),
 ('dock_tub',dk,SH),('dock_back',db,SH),('dock_seal',dseal,(0.88,0.38,0.11)),('pogo_ring_tpu',ring,(0.05,0.05,0.05)),
 ('mosfet_fowecry_99x52',mos,(0.15,0.25,0.6)),('pogo_pcb',pogo_pcb,(0.1,0.3,0.15)),('pogo_strips',pogo_body,(0.08,0.08,0.09)),('pogo_pins',pogo,(0.85,0.65,0.2)),('magnets_head_12x3',mag_h,(0.75,0.76,0.8)),('magnets_dock_12x3',mag_d,(0.75,0.76,0.8)),('dowels_4mm',dowels,(0.85,0.86,0.88)),
 ('gps_atgm336h',grx,(0.2,0.45,0.25)),('gps_antenna_est',ant,(0.75,0.55,0.4)),('buck_5v_est',buck,(0.1,0.5,0.2)),
 ('grommet_tpu',grommet,(0.05,0.05,0.05)),('loom_cable',cable,(0.05,0.05,0.05)),('dock_cap',cap,SH)]
asm=cq.Assembly(name="xl-dash-dock-idea-v2")
for n,w,c in items:
    if n!='dock_cap': asm.add(rot(w),name=n,color=C(*c))
asm.save(OUT+'xl-dash-dock-v2-assembly.step')
for n,w in (('head-front',front),('head-back',hb),('head-seal',hseal),('dock-tub',dk),('dock-back',db),('dock-seal',dseal),('pogo-ring',ring),('dock-cap',cap)):
    cq.exporters.export(rot(w),OUT+f'xl-dash-dock-v2-{n}.step')
    cq.exporters.export(rot(w),OUT+f'xl-dash-dock-v2-{n}.stl',tolerance=0.05,angularTolerance=0.2)
os.makedirs(OUT+'parts',exist_ok=True)
for n,w,c in items: cq.exporters.export(rot(w),OUT+f'parts/{n}.stl',tolerance=0.05,angularTolerance=0.25)
for n,a in (('head',head_shell),('dock',dock_shell)):
    bb=rot(a).val().BoundingBox();print(n,'bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f'%(bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax))
