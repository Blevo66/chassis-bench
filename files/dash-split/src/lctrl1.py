# LEFT BAR CONTROLLER housing v1 (2026-11-25, Joel: bars 22.2 mm, MCP23017 chip stays in the controller).
# Axes: X along the bar (+X = outboard, toward the grip), Y forward (+Y = away from the rider), Z up. Bar centre at origin.
# Parts: MAIN BODY (button face toward the rider, open bottom), FRONT CLAMP CAP (2x M4 into heat-sets, above and below
# the bar), BOTTOM LID (MCP23017 board on 2 posts, cable gland + drain), TPU lid seal.
# Buttons = generic IP67 12 mm momentary: cap/flange 15 dia x 3 outside, nut ~16 x 3 inside, body 13 dia x 22 + tags 5.
# ALL button, board and gland sizes are GUESSES until Joel picks parts. Clutch perch position unknown: housing assumed
# to sit just inboard of it (no perch modelled).
import cadquery as cq, os
SCR='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/'
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
BR=22.2/2; W=2.5
XW=26.0                       # half width along the bar
YR,YF=-42.0,16.0              # rider face, front of cap
ZB,ZT=-44.0,32.0
LID=2.5
def rbox(x0,x1,y0,y1,z0,z1,r):
    b=box(x0,x1,y0,y1,z0,z1)
    try: b=b.edges("|Z").fillet(r)
    except Exception as e: print('fillet',e)
    return b
outer=rbox(-XW,XW,YR,YF,ZB,ZT,6.0)
try: outer=outer.faces(">Z").edges().fillet(4.0)
except Exception as e: print('top fillet',e)
bar=cq.Workplane("YZ").workplane(offset=-60).circle(BR+0.15).extrude(120)
barvis=cq.Workplane("YZ").workplane(offset=-60).circle(BR).extrude(120)
# split: front cap = Y>0 between Z -20..20 ; lid = Z<ZB+LID
capzone=box(-40,40,0,40,-20,20)
lidzone=box(-40,40,-60,0,ZB-1,ZB+LID)
body=outer.cut(capzone).cut(lidzone)
cap=outer.intersect(capzone)
lid=outer.intersect(lidzone)
# body below/above the cap (Y>0, |Z|>20) stays as part of the body: trim it back so the cap clamps cleanly
body=body.cut(box(-40,40,0.0,40,-60,-20)).cut(box(-40,40,0.0,40,20,60))
body=body.cut(bar); cap=cap.cut(bar)
# cavity: everything behind the bar saddle
cav=box(-XW+W,XW-W,YR+W,-13.5,ZB+LID-1,ZT-W)
body=body.cut(cav)
# clamp screws: M4 from the front through the cap into heat-sets in the body (Y -8..0) at Z +/-15.5, X +/-17
SCW=[(-17,15.5),(17,15.5),(-17,-15.5),(17,-15.5)]
for x,z in SCW:
    cap=cap.cut(cq.Workplane("XZ").workplane(offset=-YF-1).center(x,z).circle(2.2).extrude(YF+2))
    cap=cap.cut(cq.Workplane("XZ").workplane(offset=-YF-1).center(x,z).circle(3.8).extrude(4.0))   # head counterbore
    body=body.cut(cq.Workplane("XZ").workplane(offset=-0.5).center(x,z).circle(2.8).extrude(9.0))   # M4 heat-set, 8 deep
# grip strip: 0.6 mm relief in the bore so it clamps on two lands (helps hold on a slick bar)
# buttons on the rider face (Y=YR), facing -Y
BT=[('horn',0,-26),('ind_l',-12,-5),('ind_r',12,-5),('lights',-12,17),('mode',12,17)]
btn=None
for n,x,z in BT:
    body=body.cut(cq.Workplane("XZ").workplane(offset=-YR+1).center(x,z).circle(6.1).extrude(-(W+2)))
    b=(cq.Workplane("XZ").workplane(offset=-YR+3).center(x,z).circle(7.5).extrude(-3)            # cap/flange outside
       .union(cq.Workplane("XZ").workplane(offset=-YR).center(x,z).circle(6.0).extrude(-W))         # thread through wall
       .union(cq.Workplane("XZ").workplane(offset=-YR-W).center(x,z).polygon(6,16/0.866).extrude(-3)) # nut
       .union(cq.Workplane("XZ").workplane(offset=-YR-W-3).center(x,z).circle(6.5).extrude(-17))    # body
       .union(cq.Workplane("XZ").workplane(offset=-YR-W-20).center(x,z).rect(8,3).extrude(-4.5)))   # tags
    btn=b if btn is None else btn.union(b)
# labels recessed 0.4 next to buttons? keep face clean; raised horn ring instead
body=body.union(cq.Workplane("XZ").workplane(offset=-YR+0.01).center(0,-26).circle(11.0).circle(9.0).extrude(1.2))
# lid: 4 corner screws into bosses, board posts, cable gland, drain
LS=[(-XW+6,YR+6),(XW-6,YR+6),(-XW+6,-17),(XW-6,-17)]
for x,y in LS:
    body=body.union(cq.Workplane("XY").workplane(offset=ZB+LID-0.01).center(x,y).circle(3.4).extrude(12))
    body=body.cut(cq.Workplane("XY").workplane(offset=ZB+LID-1).center(x,y).circle(2.0).extrude(9))
    lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(1.7).extrude(5)).cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(3.1).extrude(1.6))
# MCP23017 breakout ~ 25 x 30 x 1.6 + ~4 parts (GUESS), on 2 posts 4 tall, long side along Y
BX0,BY0=-14.0,-38.8
for x,y in ((BX0+4,BY0+5),(BX0+26,BY0+20)):
    lid=lid.union(cq.Workplane("XY").workplane(offset=ZB+LID-0.01).center(x,y).circle(2.6).extrude(2.0))
mcp=box(BX0,BX0+30,BY0,BY0+25,ZB+LID+2,ZB+LID+2+1.6).union(box(BX0+4,BX0+26,BY0+3,BY0+22,ZB+LID+3.6,ZB+LID+7.0))   # 30 x 25 along X
# cable: 5 mm 4-core through a printed TPU grommet (no thread) in the lid, toward the bar end of the box
GX,GY=-18.0,-26.5
lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(GX,GY).circle(4.0).extrude(LID+2))
grom=(cq.Workplane("XY").workplane(offset=ZB-6).center(GX,GY).circle(5.5).circle(2.4).extrude(6.0)
      .union(cq.Workplane("XY").workplane(offset=ZB).center(GX,GY).circle(4.0).circle(2.4).extrude(LID))
      .union(cq.Workplane("XY").workplane(offset=ZB+LID).center(GX,GY).circle(5.0).circle(2.4).extrude(1.5)))
cable=cq.Workplane("XY").workplane(offset=ZB-40).center(GX,GY).circle(2.5).extrude(40+LID+6)
lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(16,-20).circle(1.5).extrude(LID+2))   # drain
seal=box(-XW+W+0.3,XW-W-0.3,YR+W+0.3,-13.8,ZB+LID,ZB+LID+1.0).cut(box(-XW+W+1.5,XW-W-1.5,YR+W+1.5,-15.0,ZB,ZB+LID+3))
seal=seal.cut(cq.Workplane("XY").workplane(offset=ZB).center(GX,GY).circle(5.5).extrude(4))
for x,y in LS: seal=seal.cut(cq.Workplane("XY").workplane(offset=ZB).center(x,y).circle(3.6).extrude(4))
parts={'buttons_12mm_x5':btn,'mcp23017_breakout':mcp,'cable_4core':cable,'grommet_tpu':grom,'bar_22_2':barvis}
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
shell=body.union(cap).union(lid)
print('valid',body.val().isValid(),cap.val().isValid(),lid.val().isValid())
for n,p in parts.items():
    v=vol(shell,p); print('%-18s shell %.2f'%(n,v))
    if v>0.3:
        for so in shell.intersect(p).solids().vals():
            b=so.BoundingBox(); print('   at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))
    for m,q in parts.items():
        if m>n:
            v=vol(p,q)
            if v>0.05: print('   clash',n,m,round(v,1))
print('seal vs body %.2f lid %.2f'%(vol(seal,body),vol(seal,lid)))
for so in seal.intersect(lid).solids().vals():
    b=so.BoundingBox(); print('  seal/lid at x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))
bb=shell.val().BoundingBox(); print('bbox %.1f x %.1f x %.1f'%(bb.xlen,bb.ylen,bb.zlen))
print('mass g (solid ASA 1.07):',round(shell.val().Volume()*1.07/1000,1))
OUT=SCR+'cad4/lctrl1/'; os.makedirs(OUT,exist_ok=True)
for n,w in (('body',body),('clamp-cap',cap),('lid',lid),('seal',seal)):
    cq.exporters.export(w,OUT+f'xl-left-controller-v1-{n}.step'); cq.exporters.export(w,OUT+f'xl-left-controller-v1-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(w,OUT+f'part-{n}.stl')
asm=cq.Assembly(name='xl-left-controller-v1')
for n,w,c in (('body',body,(0.13,0.15,0.17)),('clamp_cap',cap,(0.13,0.15,0.17)),('lid',lid,(0.13,0.15,0.17)),('seal',seal,(0.88,0.38,0.11))): asm.add(w,name=n,color=cq.Color(*c))
cols={'buttons_12mm_x5':(0.7,0.7,0.72),'mcp23017_breakout':(0.1,0.3,0.7),'cable_4core':(0.08,0.08,0.08),'grommet_tpu':(0.88,0.38,0.11),'bar_22_2':(0.55,0.56,0.58)}
for n,w in parts.items(): asm.add(w,name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-left-controller-v1-assembly.step')
