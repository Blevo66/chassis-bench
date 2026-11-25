# v3 (2026-11-25, Joel: 'the plug on the control box doesn't have to be flush anymore so it can stick out'):
# AMPSEAL header now mounts from OUTSIDE: shroud + flange proud of the plug-side wall, TPU gasket between flange and wall,
# printed retainer frame over the flange. Only its rear body (16 mm) is inside, so the thick wall block goes, the box
# loses 21 mm across the bike and the plug end drops from 40 to 33 mm tall.
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
# v2 (Joel: "slim the brain box down behind the plugs"): full 40 mm height only over the plug end (y < YS),
# a 45 deg ramp, then 29 mm over the rest. PCA9685 moves UNDER the MOSFET board (board on 7.5 mm standoffs),
# 5 V buck moves into the plug end. Lid = 2.5 mm stepped shell; split surface follows the top 2.5 mm down,
# so the rim (and its TPU seal) steps down the 45 deg ramp in the side walls.
L,Y0,Y1=105.0,-29.0,60.0                 # 105 long x 89 wide
HT,HS,YS=33.0,29.0,-12.0                 # tall (plug end) height, slim height, start of ramp
YR=YS+(HT-HS)                            # ramp foot (45 deg)
H=HT
W=2.5; LID=2.5; R=4.0
def prof(pts,x0,x1):
    return cq.Workplane("YZ").workplane(offset=x0).polyline(pts).close().extrude(x1-x0)
def topline(dz,y0,y1):   # stepped top surface shifted down by dz, from y0 to y1
    return [(y0,HT-dz),(YS,HT-dz),(YR,HS-dz),(y1,HS-dz)]
outer=prof([(Y0,0)]+topline(0,Y0,Y1)+[(Y1,0)],0,L)
try: outer=outer.edges("|Z").fillet(R)
except Exception as e: print('outer fillet skip',e)
try: outer=outer.faces("<Z").edges().fillet(2.0)
except Exception as e: print('bottom fillet skip',e)
cav=prof([(Y0+W,W)]+topline(W,Y0+W,Y1-W)+[(Y1-W,W)],W,L-W)
try: cav=cav.edges("|Z").fillet(R-W)
except Exception as e: print('cav fillet skip',e)
above=prof([(Y0-5,HT+20)]+topline(LID,Y0-5,Y1+5)+[(Y1+5,HT+20)],-5,L+5)
base=outer.cut(above).cut(cav)
lid=outer.intersect(above).cut(cav)
try: lid=lid.faces(">Z").edges().fillet(1.2)
except Exception as e: print('lid fillet skip',e)
# ---- AMPSEAL 23 straight header, mounted from OUTSIDE: flange + gasket on the wall's outer face ----
XC,ZC=40.0,16.05                     # flange 0..32.1 tall, flush with the box floor
GK=1.0
YA=Y0-GK-22.1                        # socket face; flange 18.4..22.1 behind it, rear body 22.1..38.1
amp=cq.importers.importStep(REPO+'dash-pod-v3/parts/te-776228-1-ampseal23.stp')
amp=amp.rotate((0,0,0),(1,0,0),90).translate((XC,YA,ZC))
base=base.cut(box(XC-30.7,XC+30.7,Y0-1,Y0+W+1,ZC-10.6,ZC+14.1))               # window for the rear body (+0.3)
gasket=box(XC-30.4,XC+30.4,Y0-GK,Y0,ZC-16.05,ZC+16.05).cut(box(XC-30.7,XC+30.7,Y0-2,Y0+1,ZC-10.6,ZC+14.1))
# retainer: 3 mm frame over the flange's front face, legs down to the wall, 4x M3 into heat-sets in bosses inside the wall
FF=YA+18.4                          # flange front face
RET0,RET1=FF-3.0,FF
ret=box(XC-37.5,XC+37.5,RET0,RET1,ZC-16.0,ZC+16.0).cut(box(XC-22.4,XC+22.4,RET0-1,RET1+1,ZC-12.5,ZC+14.5))
SCR4=[(XC-34.6,ZC-11.5),(XC-34.6,ZC+11.5),(XC+34.6,ZC-11.5),(XC+34.6,ZC+11.5)]
for x,z in SCR4:
    ret=ret.union(cq.Workplane("XZ").workplane(offset=-RET1).center(x,z).circle(3.0).extrude(-(Y0-RET1)))      # leg to the wall
    ret=ret.cut(cq.Workplane("XZ").workplane(offset=-(RET0-1)).center(x,z).circle(1.7).extrude(-(Y0-RET0+2)))
    base=base.union(cq.Workplane("XZ").workplane(offset=-(Y0+W-0.01)).center(x,z).circle(3.4).extrude(-6.0))   # boss inside
    base=base.cut(cq.Workplane("XZ").workplane(offset=-(Y0-1)).center(x,z).circle(2.0).extrude(-(W+7)))
# ---- M12 12-pin socket (Hamadap) to the screen pod, same wall, rear end ----
MX,MZ=89.0,ZC
ax=lambda y0,Lh,r: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).circle(r).extrude(-Lh)
hexw=lambda y0,Lh,af: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).polygon(6,af/math.cos(math.pi/6)).extrude(-Lh)
base=base.cut(ax(Y0-1,W+2,8.1))
# Joel's Amazon Hamadap M12 12-pin A-coded back-mount socket (same part as the screen pod; nut/hex/length split ESTIMATED from his photo)
m12=(hexw(Y0+W,3.0,19.0).union(ax(Y0+W+3.0,6.0,5.0)).union(ax(Y0,W,7.9))
     .union(hexw(Y0-3.0,3.0,19.0)).union(ax(Y0-4.5,1.5,7.9)).union(ax(Y0-10.5,6.0,5.9)))
m12p=ax(Y0-4.7-14,14,10.0).union(ax(Y0-4.7-45,31,7.5)).union(ax(Y0-4.7-75,30,3.5))
# mating AMPSEAL plug (TE 770680-1), envelope GUESS: 64 x 36 body ~48 long incl. boot + 12 mm loom
ampp=box(XC-32,XC+32,YA-48,YA-0.2,ZC-18,ZC+18).union(cq.Workplane("XZ").workplane(offset=-(YA-48)).center(XC,ZC).circle(7.0).extrude(30))
# ---- MOSFET board on 4 standoffs ----
mos=cq.importers.importStep(REPO+'dash-pod-v3/parts/fowecry-mosfet-board-joel.step').rotate((0,0,0),(1,0,0),90)
BXC,BYC,BZ=L/2,25.0,W+7.5                    # 7.5 mm standoffs: PCA9685 lies under the board; board edge ~10 mm clear of the AMPSEAL pin tips for wire bends
mos=mos.translate((BXC,BYC,BZ))
for sx in (-1,1):
    for sy in (-1,1):
        x,y=BXC+sx*45.5,BYC+sy*22.0
        base=base.union(cq.Workplane("XY").workplane(offset=W-0.01).center(x,y).circle(3.2).extrude(BZ-W+0.01))
        base=base.cut(cq.Workplane("XY").workplane(offset=W-0.5).center(x,y).circle(1.4).extrude(3))   # self-tap M3 or heat-set
# ---- lid screws: 2 into the thick wall, 2 into bosses on the far wall ----
LS=[(4.5+1.5,Y0+6.0),(L-6.0,Y0+22.0),(25.0,Y1-3.5),(80.0,Y1-3.5)]
for x,y in LS:
    base=base.union(cq.Workplane("XY").workplane(offset=W).center(x,y).circle(3.4).extrude((HT if y<YS else HS)-LID-W))
for i,(x,y) in enumerate(LS):
    top=HT if i<2 else HS
    base=base.cut(cq.Workplane("XY").workplane(offset=top-LID-6.0).center(x,y).circle(2.0).extrude(6.1))
    lid=lid.cut(cq.Workplane("XY").workplane(offset=top-LID-1).center(x,y).circle(1.7).extrude(5)).cut(cq.Workplane("XY").workplane(offset=top-1.0).center(x,y).circle(3.1).extrude(2))
# TPU seal groove along the stepped rim (centreline 1.25 in from the outer face; corners R2.75 on the flat ends)
def zat(y): return HT-LID if y<=YS else (HS-LID if y>=YR else HT-LID-(y-YS))
c=1.25; rc=R-c
V=cq.Vector
pts=[]
def L3(p,q): return cq.Edge.makeLine(V(*p),V(*q))
def A3(p,m,q): return cq.Edge.makeThreePointArc(V(*p),V(*m),V(*q))
zt,zs=HT-LID,HS-LID
k=rc*(1-1/math.sqrt(2))
E=[ L3((c,Y0+R,zt),(c,YS,zt)), L3((c,YS,zt),(c,YR,zs)), L3((c,YR,zs),(c,Y1-R,zs)),
    A3((c,Y1-R,zs),(c+k,Y1-c-k,zs),(R,Y1-c,zs)), L3((R,Y1-c,zs),(L-R,Y1-c,zs)),
    A3((L-R,Y1-c,zs),(L-c-k,Y1-c-k,zs),(L-c,Y1-R,zs)), L3((L-c,Y1-R,zs),(L-c,YR,zs)), L3((L-c,YR,zs),(L-c,YS,zt)),
    L3((L-c,YS,zt),(L-c,Y0+R,zt)), A3((L-c,Y0+R,zt),(L-c-k,Y0+c+k,zt),(L-R,Y0+c,zt)), L3((L-R,Y0+c,zt),(R,Y0+c,zt)),
    A3((R,Y0+c,zt),(c+k,Y0+c+k,zt),(c,Y0+R,zt)) ]
path=cq.Wire.assembleEdges(E)
def ring(w,h,dz):   # rectangle w x h swept along the rim, its top dz above the rim
    sec=cq.Workplane(cq.Plane(origin=V(c,Y0+R,zt),xDir=V(1,0,0),normal=V(0,1,0))).center(0,dz-h/2).rect(w,h)
    return sec.sweep(cq.Workplane().add(path),transition='round')
groove=ring(1.2,1.2,0.01)
base=base.cut(groove)
seal=ring(1.0,1.5,0.4)
# breather 3 mm in the lid (PTFE vent inside)
lid=lid.cut(cq.Workplane("XY").workplane(offset=HS-LID-1).center(L-12,Y1-14).circle(1.5).extrude(5))
# boards on the lid underside (component side down), sizes typical
pca=box(22,84.5,10,35.4,W+0.8,W+0.8+3.6)            # PCA9685 ~62.5 x 25.4, header pins NOT fitted (wires soldered), ~3.6 thick, under the MOSFET board
for x,y in ((26,14),(80.5,31.4)):
    base=base.union(cq.Workplane("XY").workplane(offset=W-0.01).center(x,y).circle(2.2).extrude(0.81))
buck=box(86,102,9,29,W+0.5,W+0.5+5.0)              # 12->5 V buck ~16 x 20 (guess), on the floor under the MOSFET board
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
A=15.2; Y0F,Z0F,XOFF=144.0,-75.5,-15.5    # box x along the brace (15.2 deg), front-bottom corner at Y144/Z-75.5 (fitcheck: ~2.5 mm all round)
def toframe(w):   # box (x,y,z) -> frame: X = y+XOFF, Y = Y0F + x cos - z sin, Z = Z0F + x sin + z cos
    # build: map box axes to frame axes first (x->Y, y->X, z->Z) = mirror? use rotation Rz(+90) then fix handedness via mirror of y
    w=w.rotate((0,0,0),(0,1,0),-A)          # tilt about box y: x rises toward +z
    w=w.mirror("XZ")                         # y -> -y  (box -y plug side becomes +y before the swap)
    w=w.rotate((0,0,0),(0,0,1),90)          # x->Y, y->-X  => box y -> X after the mirror
    return w.translate((XOFF,Y0F,Z0F))
OUT=SCR+'cad4/brain3/'
import os; os.makedirs(OUT,exist_ok=True)
for n,w in (('base',base),('lid',lid),('seal',seal)):
    cq.exporters.export(w,OUT+f'xl-dash-brain-v3-{n}.step')
    cq.exporters.export(w,OUT+f'xl-dash-brain-v3-{n}.stl',tolerance=0.05,angularTolerance=0.2)
    cq.exporters.export(toframe(w),OUT+f'frame-brain-{n}.stl',tolerance=0.1,angularTolerance=0.3)
for n,w in parts.items():
    cq.exporters.export(w,OUT+f'part-{n}.stl')
    cq.exporters.export(toframe(w),OUT+f'frame-part-{n}.stl',tolerance=0.1,angularTolerance=0.3)
asm=cq.Assembly(name="xl-dash-brain-v2")
asm.add(base,name="base",color=cq.Color(0.13,0.15,0.17)); asm.add(lid,name="lid",color=cq.Color(0.13,0.15,0.17)); asm.add(seal,name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
cols={'ampseal23_776228_1':(0.12,0.12,0.12),'ampseal_gasket_tpu':(0.88,0.38,0.11),'ampseal_retainer':(0.2,0.2,0.22),'mosfet_fowecry_99x52':(0.15,0.25,0.6),'m12_socket_8pin':(0.75,0.76,0.78),'pca9685_module':(0.1,0.3,0.7),'buck_5v':(0.1,0.5,0.2),'m12_plug_straight':(0.1,0.1,0.1),'ampseal_plug_770680_est':(0.1,0.1,0.1)}
for n,p in parts.items(): asm.add(p,name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-dash-brain-v3-assembly.step')
