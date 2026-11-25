# v3 (2026-11-25, Joel: 'No, a vertical arc - and make the housing suit it more'): rows 1-2-2 (lights / ind L+R /
# mode+horn) with each row's centre on a VERTICAL arc (R35, bowing toward the rider's thumb side), and the housing
# outline = rounded hull of the buttons (12 mm margin) plus a small chin for the MCP board. Cable bay behind the board.
# v2 (2026-11-25, Joel: 'arrange the 5 buttons in an arc, indicators side by side, one above and two below'):
# buttons on an ARCH, radius 26 about (0,ZC): lights top, ind L/R either side, mode + horn underneath (horn on the
# outboard/thumb side with a raised ring). Box widened to 72 to fit the arch.
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
import math
YR,YF=-42.0,16.0              # rider face, front of cap
LID=2.5
# ---- button layout: 1-2-2 rows, row centres on a vertical arc ----
RA,XC=35.0,33.0               # arc radius, arc centre X (centre at Z=0, on the thumb/outboard side)
def rowx(z): return XC-math.sqrt(RA*RA-z*z)
ZR=[22.0,0.0,-22.0]; PAIR=12.0
BT=[('lights',rowx(22),22.0),('ind_l',rowx(0)-PAIR,0.0),('ind_r',rowx(0)+PAIR,0.0),('mode',rowx(-22)-PAIR,-22.0),('horn',rowx(-22)+PAIR,-22.0)]
HX,HZ=BT[4][1],BT[4][2]
print('buttons',[(n,round(x,1),z) for n,x,z in BT])
MG=12.0
pts=[(x,z) for _,x,z in BT]+[(-11.5,-27.0),(11.5,-27.0)]
def hull(P):
    P=sorted(set(P))
    def cr(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in P:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
H=hull(pts)
def prof(off):   # XZ workplane at y=YF, extruding toward -Y
    return cq.Workplane("XZ").workplane(offset=-YF).polyline(H).close().offset2D(off,'arc')
outer=prof(MG).extrude(YF-YR)
try: outer=outer.faces("<Y").edges().fillet(3.0)
except Exception as e: print('face fillet',e)
bbo=outer.val().BoundingBox(); ZB,ZT=bbo.zmin,bbo.zmax; XW=max(-bbo.xmin,bbo.xmax)
print('outline x %.1f..%.1f z %.1f..%.1f'%(bbo.xmin,bbo.xmax,ZB,ZT))
bar=cq.Workplane("YZ").workplane(offset=-60).circle(BR+0.15).extrude(120)
barvis=cq.Workplane("YZ").workplane(offset=-60).circle(BR).extrude(120)
capzone=box(-60,60,0,40,-20,20)
lidzone=box(-60,60,-60,0,ZB-1,ZB+LID)
body=outer.cut(capzone).cut(lidzone)
cap=outer.intersect(capzone)
lid=outer.intersect(lidzone)
body=body.cut(box(-60,60,0.0,40,-80,-20)).cut(box(-60,60,0.0,40,20,80))
body=body.cut(bar); cap=cap.cut(bar)
cav=prof(MG-W).extrude(YF-YR).intersect(box(-60,60,YR+W,-13.5,ZB+LID-1,80))
body=body.cut(cav)
BAY=box(-6.5,6.5,-16.0,-2.0,ZB+LID-1,ZB+LID+9)          # cable bay behind the board, down to the lid grommet
body=body.cut(BAY)
# clamp screws: M4 from the front through the cap into heat-sets in the body (Y -8..0) at Z +/-15.5, X +/-17
SCW=[(-8,15.5),(12,15.5),(-14,-15.5),(14,-15.5)]   # kept inside the outline
for x,z in SCW:
    cap=cap.cut(cq.Workplane("XZ").workplane(offset=-YF-1).center(x,z).circle(2.2).extrude(YF+2))
    cap=cap.cut(cq.Workplane("XZ").workplane(offset=-YF-1).center(x,z).circle(3.8).extrude(4.0))   # head counterbore
    body=body.cut(cq.Workplane("XZ").workplane(offset=-0.5).center(x,z).circle(2.8).extrude(9.0))   # M4 heat-set, 8 deep
# grip strip: 0.6 mm relief in the bore so it clamps on two lands (helps hold on a slick bar)
# buttons on the rider face (Y=YR), facing -Y
def arc(deg): return (round(RA*math.cos(math.radians(deg)),2), round(ZC+RA*math.sin(math.radians(deg)),2))
# +X = outboard (grip/thumb side). Angles measured from +X.
btn=None
for n,x,z in BT:
    body=body.cut(cq.Workplane("XZ").workplane(offset=-YR+1).center(x,z).circle(6.1).extrude(-(W+2)))
    b=(cq.Workplane("XZ").workplane(offset=-YR+3).center(x,z).circle(7.5).extrude(-3)            # cap/flange outside
       .union(cq.Workplane("XZ").workplane(offset=-YR).center(x,z).circle(6.0).extrude(-W))         # thread through wall
       .union(cq.Workplane("XZ").workplane(offset=-YR-W).center(x,z).polygon(6,16/0.866).extrude(-3)) # nut
       .union(cq.Workplane("XZ").workplane(offset=-YR-W-3).center(x,z).circle(6.5).extrude(-17))    # body
       .union(cq.Workplane("XZ").workplane(offset=-YR-W-20).center(x,z).rect(8,3).extrude(-4.5)))   # tags
    BTS=globals().setdefault('BTS',[]); BTS.append((n,b))
    btn=b if btn is None else btn.union(b)
# labels recessed 0.4 next to buttons? keep face clean; raised horn ring instead
body=body.union(cq.Workplane("XZ").workplane(offset=-YR+0.01).center(HX,HZ).circle(11.0).circle(9.0).extrude(1.2))
# lid: 4 corner screws into bosses, board posts, cable gland, drain
LS=[(-15.2,-27.0),(15.2,-27.0)]
for x,y in LS:
    body=body.union(cq.Workplane("XY").workplane(offset=ZB+LID-0.01).center(x,y).circle(3.2).extrude(7))
    body=body.cut(cq.Workplane("XY").workplane(offset=ZB+LID-1).center(x,y).circle(2.0).extrude(6.5))
    lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(1.7).extrude(5)).cut(cq.Workplane("XY").workplane(offset=ZB-1).center(x,y).circle(3.1).extrude(1.6))
# MCP23017 breakout ~ 25 x 30 x 1.6 + ~4 parts (GUESS), on 2 posts 4 tall, long side along Y
BX0,BY0=-11.5,-36.5
for x,y in ((BX0+3,BY0+3),(BX0+20.5,BY0+15)):
    lid=lid.union(cq.Workplane("XY").workplane(offset=ZB+LID-0.01).center(x,y).circle(2.6).extrude(2.0))
mcp=box(BX0,BX0+23,BY0,BY0+18,ZB+LID+2,ZB+LID+2+1.6).union(box(BX0+3,BX0+20,BY0+2,BY0+16,ZB+LID+3.6,ZB+LID+6.5))   # small 23 x 18 MCP23017 board (GUESS)
# cable: 5 mm 4-core through a printed TPU grommet (no thread) in the lid, toward the bar end of the box
GX,GY=0.0,-8.5
lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(GX,GY).circle(4.0).extrude(LID+2))
grom=(cq.Workplane("XY").workplane(offset=ZB-6).center(GX,GY).circle(5.5).circle(2.4).extrude(6.0)
      .union(cq.Workplane("XY").workplane(offset=ZB).center(GX,GY).circle(4.0).circle(2.4).extrude(LID))
      .union(cq.Workplane("XY").workplane(offset=ZB+LID).center(GX,GY).circle(5.0).circle(2.4).extrude(1.5)))
cable=cq.Workplane("XY").workplane(offset=ZB-40).center(GX,GY).circle(2.5).extrude(40+LID+5)
lid=lid.cut(cq.Workplane("XY").workplane(offset=ZB-1).center(0,-39.0).circle(1.5).extrude(LID+2))   # drain at the rider-side edge
# seal: TPU ring under the body walls at the lid split (inset 0.8..2.0 from the outline at that height)
_sb=outer.intersect(box(-60,60,-60,0,ZB+LID-0.01,ZB+LID+0.01)).val().BoundingBox()
def _rr(x0,x1,y0,y1,r,z0,z1): return cq.Workplane("XY").workplane(offset=z0).center((x0+x1)/2,(y0+y1)/2).placeSketch(cq.Sketch().rect(x1-x0,y1-y0).vertices().fillet(r)).extrude(z1-z0)
GRV=0.8
seal=_rr(_sb.xmin+0.8,_sb.xmax-0.8,_sb.ymin+0.8,-0.8,5.0,ZB+LID-GRV,ZB+LID+0.5).cut(_rr(_sb.xmin+2.0,_sb.xmax-2.0,_sb.ymin+2.0,-2.0,4.0,ZB,ZB+LID+2))
body=body.cut(_rr(_sb.xmin+0.7,_sb.xmax-0.7,_sb.ymin+0.7,-0.7,5.1,ZB+LID-0.01,ZB+LID+0.3).cut(_rr(_sb.xmin+2.1,_sb.xmax-2.1,_sb.ymin+2.1,-2.1,3.9,ZB,ZB+LID+2)))   # groove in body
lid=lid.cut(_rr(_sb.xmin+0.7,_sb.xmax-0.7,_sb.ymin+0.7,-0.7,5.1,ZB+LID-GRV,ZB+LID+0.1).cut(_rr(_sb.xmin+2.1,_sb.xmax-2.1,_sb.ymin+2.1,-2.1,3.9,ZB,ZB+LID+2)))  # shallow groove in lid
for x,y in LS: seal=seal.cut(cq.Workplane("XY").workplane(offset=ZB).center(x,y).circle(3.6).extrude(5))
parts={'buttons_12mm_x5':btn,'mcp23017_breakout':mcp,'cable_4core':cable,'grommet_tpu':grom,'bar_22_2':barvis}
def vol(a,b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
shell=body.union(cap).union(lid)
for i in range(len(BTS)):
    for j in range(i+1,len(BTS)):
        try: v=BTS[i][1].intersect(BTS[j][1]).val().Volume()
        except Exception: v=0
        if v>0.01: print('   button clash',BTS[i][0],BTS[j][0],round(v,2))
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
OUT=SCR+'cad4/lctrl3/'; os.makedirs(OUT,exist_ok=True)
for n,w in (('body',body),('clamp-cap',cap),('lid',lid),('seal',seal)):
    cq.exporters.export(w,OUT+f'xl-left-controller-v3-{n}.step'); cq.exporters.export(w,OUT+f'xl-left-controller-v3-{n}.stl',tolerance=0.05,angularTolerance=0.2)
for n,w in parts.items(): cq.exporters.export(w,OUT+f'part-{n}.stl')
asm=cq.Assembly(name='xl-left-controller-v3')
for n,w,c in (('body',body,(0.13,0.15,0.17)),('clamp_cap',cap,(0.13,0.15,0.17)),('lid',lid,(0.13,0.15,0.17)),('seal',seal,(0.88,0.38,0.11))): asm.add(w,name=n,color=cq.Color(*c))
cols={'buttons_12mm_x5':(0.7,0.7,0.72),'mcp23017_breakout':(0.1,0.3,0.7),'cable_4core':(0.08,0.08,0.08),'grommet_tpu':(0.88,0.38,0.11),'bar_22_2':(0.55,0.56,0.58)}
for n,w in parts.items(): asm.add(w,name=n,color=cq.Color(*cols[n]))
asm.save(OUT+'xl-left-controller-v3-assembly.step')
