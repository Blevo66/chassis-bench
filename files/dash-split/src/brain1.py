# XL dash v4 SPLIT: BRAIN BOX for the frame triangle under the tank (Joel 2026-11-25: "slim and rectangular",
# straight AMPSEAL on one end, screen gets an M12 side plug).
# Box-local axes: x along the box (rearward, follows the brace), y across the bike (-y = plug side), z up off the brace.
# Contents: Joel's Fowecry MOSFET board (his STEP) flat on the floor, TE AMPSEAL 23 straight header 776228-1
# (TE's STEP) flush in the plug-side wall, M12 8-pin socket to the screen pod beside it, PCA9685 + 5 V buck on the lid.
# Wires solder straight onto the AMPSEAL pins (no breakout PCB).  Sizes of PCA9685, buck, M12 and the mating
# AMPSEAL plug are TYPICAL / GUESSED.
import cadquery as cq, math, json
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
REPO='/home/user/chassis-bench/files/'
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
L,Y0,Y1,H=105.0,-50.0,60.0,40.0          # outer box: 105 long x 110 wide x 40 tall
W=2.5; LID=2.5; R=4.0
def rbox(x0,x1,y0,y1,z0,z1,r):
    return cq.Workplane("XY").workplane(offset=z0).center((x0+x1)/2,(y0+y1)/2).sketch().rect(x1-x0,y1-y0).vertices().fillet(r).finalize().extrude(z1-z0)
base=rbox(0,L,Y0,Y1,0,H-LID,R)
try: base=base.faces("<Z").edges().fillet(2.0)
except Exception as e: print('base fillet skip',e)
base=base.cut(rbox(W,L-W,Y0+W,Y1-W,W,H,R-W))
lid=rbox(0,L,Y0,Y1,H-LID,H,R)
try: lid=lid.faces(">Z").edges().fillet(1.5)
except Exception as e: print('lid fillet skip',e)
# ---- AMPSEAL 23 straight header, socket face flush with the y=Y0 wall ----
XC,ZC=40.0,20.0
amp=cq.importers.importStep(REPO+'dash-pod-v3/parts/te-776228-1-ampseal23.stp')
amp=amp.rotate((0,0,0),(1,0,0),90).translate((XC,Y0,ZC))       # hx->x, hy->z, hz(mating, body -z)->+y
FY0=Y0+18.5; FY1=Y0+22.0; GK=1.0
blk=box(W,77.5,Y0+W-0.01,FY0-GK,W-0.01,H-LID)                    # thick wall around the socket shroud
base=base.union(blk)
base=base.cut(box(XC-21.9,XC+21.9,Y0-1,FY0-GK+0.01,ZC-12.0,ZC+12.0))          # socket hole (+0.2)
base=base.cut(box(XC-5.5,XC+5.5,Y0-1,Y0+7.5,ZC+11.5,ZC+16.3))                 # latch-arm slot over the ramp
ch=(cq.Workplane("XZ").workplane(offset=-(Y0-0.01)).center(XC,ZC).rect(45.4,25.6).workplane(offset=-0.81).rect(43.8,24.0).loft())
base=base.cut(ch)
gasket=box(XC-30.4,XC+30.4,FY0-GK,FY0,ZC-16.05,ZC+16.05).cut(box(XC-21.7,XC+21.7,FY0-2,FY0+1,ZC-11.8,ZC+11.8))
# retainer frame behind the flange, 4x M3 into heat-sets in standoffs on the thick wall
RET0,RET1=FY1,FY1+3.0
ret=box(XC-37.5,XC+37.5,RET0,RET1,ZC-16.0,ZC+16.0).cut(box(XC-28.4,XC+28.4,RET0-1,RET1+1,ZC-10.5,ZC+14.0))
for sx in (-1,1):
    for z0,z1 in ((ZC-8.7,ZC-5.9),(ZC+9.4,ZC+12.2)):
        ret=ret.cut(box(min(XC+sx*27.9,XC+sx*30.8),max(XC+sx*27.9,XC+sx*30.8),RET0-1,RET1+1,z0,z1))   # notches for ribs on the header's rear body
SCR4=[(XC-34.6,ZC-11.5),(XC-34.6,ZC+11.5),(XC+34.6,ZC-11.5),(XC+34.6,ZC+11.5)]
for x,z in SCR4:
    base=base.union(cq.Workplane("XZ").workplane(offset=-(FY0-GK)).center(x,z).circle(3.4).extrude(-(RET0-(FY0-GK))))
    base=base.cut(cq.Workplane("XZ").workplane(offset=-(RET0-5.5)).center(x,z).circle(2.0).extrude(-6))
    ret=ret.cut(cq.Workplane("XZ").workplane(offset=-(RET0-1)).center(x,z).circle(1.7).extrude(-6))
# ---- M12 8-pin socket to the screen pod, same wall, rear end ----
MX,MZ=89.0,ZC
ax=lambda y0,Lh,r: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).circle(r).extrude(-Lh)
hexw=lambda y0,Lh,af: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).polygon(6,af/math.cos(math.pi/6)).extrude(-Lh)
base=base.cut(ax(Y0-1,W+2,8.1))
m12=(ax(Y0-8.0,6.0,6.0).union(ax(Y0-2.0,2.0,10.0)).union(ax(Y0,W+0.4,7.9))
     .union(hexw(Y0+W+0.4,3.0,20.0)).union(ax(Y0+W+3.4,12.0,6.5)))
m12p=ax(Y0-22.0,14,10.0).union(ax(Y0-53.0,31,7.5)).union(ax(Y0-83.0,30,3.5))
# mating AMPSEAL plug (TE 770680-1), envelope GUESS: 64 x 36 body ~48 long incl. boot + 12 mm loom
ampp=box(XC-32,XC+32,Y0-48,Y0-0.2,ZC-18,ZC+18).union(cq.Workplane("XZ").workplane(offset=-(Y0-48)).center(XC,ZC).circle(7.0).extrude(30))
# ---- MOSFET board on 4 standoffs ----
mos=cq.importers.importStep(REPO+'dash-pod-v3/parts/fowecry-mosfet-board-joel.step').rotate((0,0,0),(1,0,0),90)
BXC,BYC,BZ=L/2,25.0,W+2.0                    # board edge ~10 mm clear of the AMPSEAL pin tips for wire bends
mos=mos.translate((BXC,BYC,BZ))
for sx in (-1,1):
    for sy in (-1,1):
        x,y=BXC+sx*45.5,BYC+sy*22.0
        base=base.union(cq.Workplane("XY").workplane(offset=W-0.01).center(x,y).circle(3.2).extrude(BZ-W+0.01))
        base=base.cut(cq.Workplane("XY").workplane(offset=W-0.5).center(x,y).circle(1.4).extrude(3))   # self-tap M3 or heat-set
# ---- lid screws: 2 into the thick wall, 2 into bosses on the far wall ----
LS=[(20.0,Y0+9.0),(62.0,Y0+9.0),(25.0,Y1-3.5),(80.0,Y1-3.5)]
for x,y in LS[2:]:
    base=base.union(cq.Workplane("XY").workplane(offset=W).center(x,y).circle(3.4).extrude(H-LID-W))
for x,y in LS:
    base=base.cut(cq.Workplane("XY").workplane(offset=H-LID-6.0).center(x,y).circle(2.0).extrude(6.1))
    lid=lid.cut(cq.Workplane("XY").workplane(offset=H-LID-1).center(x,y).circle(1.7).extrude(5)).cut(cq.Workplane("XY").workplane(offset=H-1.0).center(x,y).circle(3.1).extrude(2))
# TPU seal groove round the base rim
base=base.cut(rbox(0.8,L-0.8,Y0+0.8,Y1-0.8,H-LID-1.2,H-LID+0.1,R-0.8).cut(rbox(2.0,L-2.0,Y0+2.0,Y1-2.0,H-LID-2,H,R-2.0)))
seal=rbox(0.9,L-0.9,Y0+0.9,Y1-0.9,H-LID-1.0,H-LID+0.4,R-0.9).cut(rbox(1.9,L-1.9,Y0+1.9,Y1-1.9,H-LID-2,H,R-1.9))
# breather 3 mm in the lid (PTFE vent inside)
lid=lid.cut(cq.Workplane("XY").workplane(offset=H-LID-1).center(L-12,Y1-14).circle(1.5).extrude(5))
# boards on the lid underside (component side down), sizes typical
pca=box(22,84.5,12,37.4,H-LID-9.0,H-LID-1.0)       # PCA9685 16-ch PWM module ~62.5 x 25.4 (Adafruit size), 8 tall incl. headers
buck=box(86,102,14,35,H-LID-6.0,H-LID-1.0)        # 12->5 V 3 A buck ~16 x 21 (guess)
for x,y in ((24,14),(82.5,35.4)):
    lid=lid.union(cq.Workplane("XY").workplane(offset=H-LID).center(x,y).circle(2.6).extrude(-1.0))
parts={'ampseal23_776228_1':amp,'ampseal_gasket_tpu':gasket,'ampseal_retainer':ret,'mosfet_fowecry_99x52':mos,
       'm12_socket_8pin':m12,'pca9685_module':pca,'buck_5v':buck,'m12_plug_straight':m12p,'ampseal_plug_770680_est':ampp}
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
shell=base.union(lid)
print('base valid',base.val().isValid(),'lid valid',lid.val().isValid())
for n,p in parts.items():
    v=vol(shell,p); print('%-26s shell %.1f'%(n,v))
    if v>0.5:
        for so in shell.intersect(p).solids().vals():
            b=so.BoundingBox(); print('     at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))
    for m,q in parts.items():
        if m>n:
            v=vol(p,q)
            if v>0.05:
                print('   clash',n,m,round(v,1))
                for so in p.intersect(q).solids().vals():
                    b=so.BoundingBox(); print('       at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))
print('box mass est PETG solid g:',round((base.val().Volume()+lid.val().Volume())*1.27/1000,1))
# ---- place in the frame (clean model coords: X right, Y rearward, Z up, origin steering axis at head-tube bottom) ----
A=15.2; Y0F,Z0F,XOFF=144.0,-75.5,-5.0     # box x along the brace (15.2 deg), front-bottom corner at Y144/Z-75.5 (fitcheck: ~2.5 mm all round)
def toframe(w):   # box (x,y,z) -> frame: X = y+XOFF, Y = Y0F + x cos - z sin, Z = Z0F + x sin + z cos
    # build: map box axes to frame axes first (x->Y, y->X, z->Z) = mirror? use rotation Rz(+90) then fix handedness via mirror of y
    w=w.rotate((0,0,0),(0,1,0),-A)          # tilt about box y: x rises toward +z
    w=w.mirror("XZ")                         # y -> -y  (box -y plug side becomes +y before the swap)
    w=w.rotate((0,0,0),(0,0,1),90)          # x->Y, y->-X  => box y -> X after the mirror
    return w.translate((XOFF,Y0F,Z0F))
OUT=SCR+'cad4/brain1/'
import os; os.makedirs(OUT,exist_ok=True)
for n,w in (('base',base),('lid',lid),('seal',seal)):
    cq.exporters.export(w,OUT+f'xl-dash-brain-v1-{n}.step')
    cq.exporters.export(w,OUT+f'xl-dash-brain-v1-{n}.stl',tolerance=0.05,angularTolerance=0.2)
    cq.exporters.export(toframe(w),OUT+f'frame-brain-{n}.stl',tolerance=0.1,angularTolerance=0.3)
for n,w in parts.items():
    cq.exporters.export(w,OUT+f'part-{n}.stl')
    cq.exporters.export(toframe(w),OUT+f'frame-part-{n}.stl',tolerance=0.1,angularTolerance=0.3)
asm=cq.Assembly(name="xl-dash-brain-v1")
asm.add(base,name="base",color=cq.Color(0.13,0.15,0.17)); asm.add(lid,name="lid",color=cq.Color(0.13,0.15,0.17)); asm.add(seal,name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
cols={'ampseal23_776228_1':(0.12,0.12,0.12),'ampseal_gasket_tpu':(0.88,0.38,0.11),'ampseal_retainer':(0.2,0.2,0.22),'mosfet_fowecry_99x52':(0.15,0.25,0.6),'m12_socket_8pin':(0.75,0.76,0.78),'pca9685_module':(0.1,0.3,0.7),'buck_5v':(0.1,0.5,0.2),'m12_plug_straight':(0.1,0.1,0.1),'ampseal_plug_770680_est':(0.1,0.1,0.1)}
for n,p in parts.items(): asm.add(p,name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-dash-brain-v1-assembly.step')
