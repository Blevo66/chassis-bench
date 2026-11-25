# XL dash BRAIN BOX v4 (2026-11-25, Joel: "make the ampseal plug go in the end of the unit" + "ignore living in the triangle").
# Free-standing box, no frame fit. AMPSEAL 23 straight header 776228-1 in the FRONT END wall (x=0), mounted from outside
# (flange + 1 mm TPU gasket on the outer face, printed retainer frame, 4x M3 into heat-sets). Hamadap M12 12-pin socket to the
# screen pod in the LEFT side wall near the far end, its body in the strip beside the MOSFET board.
# Board 99 long runs along the box behind a 10 mm wire-bend gap after the AMPSEAL tails. PCA9685 + 5 V buck under the board.
# Box axes: x along the box (AMPSEAL end at x=0), y across (-y = M12 side), z up. Sizes of PCA9685, buck, M12 nut and the
# mating AMPSEAL plug are TYPICAL / GUESSED.
import cadquery as cq, math, os
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
REPO='/home/user/chassis-bench/files/'
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def rr(w,h,r): return cq.Sketch().rect(w,h).vertices().fillet(r)
def slab(cx,cy,w,h,r,z0,z1): return cq.Workplane("XY").workplane(offset=z0).center(cx,cy).placeSketch(rr(w,h,r)).extrude(z1-z0)
W=2.5; LID=2.5; R=4.0
L,WD,H=132.0,82.0,33.0                    # 132 long x 82 wide x 33 tall
CX=L/2
outer=slab(CX,0,L,WD,R,0,H)
try: outer=outer.faces("<Z").edges().fillet(2.0)
except Exception as e: print('bottom fillet skip',e)
try: outer=outer.faces(">Z").edges().fillet(1.5)
except Exception as e: print('top fillet skip',e)
cav=slab(CX,0,L-2*W,WD-2*W,R-W,W,H-LID)
base=outer.cut(box(-5,L+5,-WD,WD,H-LID,H+5)).cut(cav)
lid=outer.intersect(box(-5,L+5,-WD,WD,H-LID,H+5))
# ---- AMPSEAL in the x=0 end wall, mounted from outside ----
ZC=16.05; GK=1.0
XA=-GK-22.1                               # socket face; flange 18.4..22.1 behind it, rear body 22.1..38.1
amp=cq.importers.importStep(REPO+'dash-pod-v3/parts/te-776228-1-ampseal23.stp')
amp=amp.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),-90).translate((XA,0,ZC))   # body runs +x into the box
base=base.cut(box(-1,W+1,-30.7,30.7,ZC-10.6,ZC+14.1))                                  # window for the rear body
gasket=box(-GK,0,-30.4,30.4,ZC-16.05,ZC+16.05).cut(box(-2,1,-30.7,30.7,ZC-10.6,ZC+14.1))
FF=XA+18.4; RET0,RET1=FF-3.0,FF
ret=box(RET0,RET1,-37.5,37.5,ZC-16.0,ZC+16.0).cut(box(RET0-1,RET1+1,-22.4,22.4,ZC-12.5,ZC+14.5))
SCR4=[(-34.6,ZC-11.5),(-34.6,ZC+11.5),(34.6,ZC-11.5),(34.6,ZC+11.5)]
for y,z in SCR4:
    ret=ret.union(cq.Workplane("YZ").workplane(offset=RET1).center(y,z).circle(3.0).extrude(-RET1))
    ret=ret.cut(cq.Workplane("YZ").workplane(offset=RET0-1).center(y,z).circle(1.7).extrude(-RET0+2))
    base=base.union(cq.Workplane("YZ").workplane(offset=W-0.01).center(y,z).circle(3.4).extrude(6.0))
    base=base.cut(cq.Workplane("YZ").workplane(offset=-1).center(y,z).circle(2.0).extrude(W+7))
ampp=box(XA-48,XA-0.2,-32,32,ZC-18,ZC+18).union(cq.Workplane("YZ").workplane(offset=XA-78).center(0,ZC).circle(7.0).extrude(30))
# ---- MOSFET board on 4 standoffs, PCA9685 + buck under it ----
BXC,BZ=W+16+10+49.5,W+7.5
mos=cq.importers.importStep(REPO+'dash-pod-v3/parts/fowecry-mosfet-board-joel.step').rotate((0,0,0),(1,0,0),90).translate((BXC,0,BZ))
for sx in (-1,1):
    for sy in (-1,1):
        x,y=BXC+sx*45.5,sy*22.0
        base=base.union(cq.Workplane("XY").workplane(offset=W-0.01).center(x,y).circle(3.2).extrude(BZ-W+0.01))
        base=base.cut(cq.Workplane("XY").workplane(offset=W-0.5).center(x,y).circle(1.4).extrude(3))
pca=box(BXC-31.25,BXC+31.25,-12.7,12.7,W+0.8,W+4.4)        # ~62.5 x 25.4, no header pins, wires soldered
buck=box(BXC-20,BXC-4,14,34,W+0.5,W+5.5)                    # 12->5 V buck ~16 x 20 (guess)
# ---- Hamadap M12 12-pin socket in the -y side wall near the far end ----
MX,MZ=L-24.0,ZC; Y0=-WD/2
ax=lambda y0,Lh,r: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).circle(r).extrude(-Lh)
hexw=lambda y0,Lh,af: cq.Workplane("XZ").workplane(offset=-y0).center(MX,MZ).polygon(6,af/math.cos(math.pi/6)).extrude(-Lh)
base=base.cut(ax(Y0-1,W+2,8.1))
m12=(hexw(Y0+W,3.0,19.0).union(ax(Y0+W+3.0,6.0,5.0)).union(ax(Y0,W,7.9))
     .union(hexw(Y0-3.0,3.0,19.0)).union(ax(Y0-4.5,1.5,7.9)).union(ax(Y0-10.5,6.0,5.9)))
m12p=ax(Y0-4.7-14,14,10.0).union(ax(Y0-4.7-45,31,7.5)).union(ax(Y0-4.7-75,30,3.5))
# ---- lid screws: 4 bosses in the corners (clear of the AMPSEAL tails and retainer bosses) ----
LS=[(14.0,-35.0),(14.0,35.0),(L-6.0,-35.0),(L-6.0,35.0)]
for x,y in LS:
    base=base.union(cq.Workplane("XY").workplane(offset=W-0.01).center(x,y).circle(3.4).extrude(H-LID-W+0.01))
    base=base.cut(cq.Workplane("XY").workplane(offset=H-LID-6.0).center(x,y).circle(2.0).extrude(6.1))
    lid=lid.cut(cq.Workplane("XY").workplane(offset=H-LID-1).center(x,y).circle(1.7).extrude(5)).cut(cq.Workplane("XY").workplane(offset=H-1.0).center(x,y).circle(3.1).extrude(2))
# ---- TPU seal: flat ring in a groove in the base rim ----
ringw=lambda w,inset,h: slab(CX,0,L-2*inset+w,WD-2*inset+w,R-inset+w/2,0,h).cut(slab(CX,0,L-2*inset-w,WD-2*inset-w,R-inset-w/2,-1,h+1))
groove=ringw(1.2,1.25,1.3).translate((0,0,H-LID-1.2))
base=base.cut(groove)
seal=ringw(1.0,1.25,1.5).translate((0,0,H-LID-1.2))   # 1.5 tall in a 1.2 groove: 0.3 squeeze
# breather 3 mm in the lid
lid=lid.cut(cq.Workplane("XY").workplane(offset=H-LID-1).center(L-20,25).circle(1.5).extrude(5))
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
            if v>0.05: print('   clash',n,m,round(v,1))
print('seal vs base',round(vol(base,seal),2),' seal vs lid',round(vol(lid,seal),2))
print('box mass est PETG solid g:',round((base.val().Volume()+lid.val().Volume())*1.27/1000,1))
bb=shell.val().BoundingBox(); print('box bbox %.1f x %.1f x %.1f'%(bb.xlen,bb.ylen,bb.zlen))
OUT=SCR+'cad4/brain4/'
os.makedirs(OUT,exist_ok=True)
for n,w in (('base',base),('lid',lid),('seal',seal)):
    cq.exporters.export(w,OUT+f'xl-dash-brain-v4-{n}.step')
    cq.exporters.export(w,OUT+f'xl-dash-brain-v4-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(w,OUT+f'part-{n}.stl')
asm=cq.Assembly(name="xl-dash-brain-v4")
asm.add(base,name="base",color=cq.Color(0.13,0.15,0.17)); asm.add(lid,name="lid",color=cq.Color(0.13,0.15,0.17)); asm.add(seal,name="tpu_seal",color=cq.Color(0.88,0.38,0.11))
cols={'ampseal23_776228_1':(0.12,0.12,0.12),'ampseal_gasket_tpu':(0.88,0.38,0.11),'ampseal_retainer':(0.2,0.2,0.22),'mosfet_fowecry_99x52':(0.15,0.25,0.6),'m12_socket_8pin':(0.75,0.76,0.78),'pca9685_module':(0.1,0.3,0.7),'buck_5v':(0.1,0.5,0.2),'m12_plug_straight':(0.1,0.1,0.1),'ampseal_plug_770680_est':(0.1,0.1,0.1)}
for n,p in parts.items(): asm.add(p,name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-dash-brain-v4-assembly.step')
