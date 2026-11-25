# AMPSEAL 23 breakout PCB for the XL dash pod (TE 776228-1 straight header).
# Writes a KiCad 7 board file; Gerbers/drill/STEP exported with kicad-cli.
# Header frame (from TE's STEP): pins on a 4 mm grid, rows y=+4 (8 pins), y=0 (7), y=-4 (8), x centred.
# Pegs (board locks) at (23.7,10.8) and (-25.2,-7.3). Flange 60.8 x 32.1.
# The PCB sits on the header's standoffs, TOP copper faces AWAY from the header (wire pads on top).
# Viewed from the top: KiCad X = -header x, KiCad Y = -header y  (KiCad Y points down).
# PIN NUMBERS match the TE footprint Joel sent (2026-11-25, component-side view): row y=+4 = 1..8, y=0 = 9..15, y=-4 = 16..23,
# each counted from header x=-14 upward. Pin 1 pad is square.
import math, sys
OUT=sys.argv[1]
W,H,RC=60.8,32.1,1.5
def K(x,y): return (round(-x,3), round(-y,3))
pins=[]
for i,x in enumerate(range(-14,15,4)): pins.append((i+1,x,4.0))
for i,x in enumerate(range(-12,13,4)): pins.append((9+i,x,0.0))
for i,x in enumerate(range(-14,15,4)): pins.append((16+i,x,-4.0))
pegs=[(23.7,10.8),(-25.2,-7.3)]
# 2026-11-25 Joel: ALL wire pads on ONE long edge (header -Y = pod -X, toward the MOSFET board: my pick).
# Routing: row y=-4 and row y=0 drop straight down on F.Cu (row 0 pins sit in the row -4 gaps);
# row y=+4 runs on B.Cu: down at x, jog +2 at y=-2 (between rows 0 and -4), down between the row -4 pins,
# then a via in its wire pad. Below y=-6 all tracks fan out at 45 deg to two staggered pad rows.
YMIN=-23.0                                   # board grows 6.95 mm on the wire side (was -16.05)
tr=[]                                        # (net, x below pin field, layer)
for n,x,y in pins:
    if y==-4.0 or y==0.0: tr.append((n,float(x),'F.Cu',x,y))
    else: tr.append((n,float(x+2),'B.Cu',x,y))
tr.sort(key=lambda t:(t[1],t[2]=='B.Cu'))
PIT=2.1; NP=len(tr); XC=1.0
YI,YO=-15.6,-19.6; PW,PH=2.4,2.4
TW=0.8
nets={p[0]:f'P{p[0]}' for p in pins}
L=[]
L.append('(kicad_pcb (version 20221018) (generator pcbnew)')
L.append(' (general (thickness 1.6))')
L.append(' (paper "A4")')
L.append(' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (40 "Dwgs.User" user "User.Drawings"))')
L.append(' (setup (pad_to_mask_clearance 0.05) (pcbplotparams (layerselection 0x00010fc_ffffffff) (outputdirectory "gerbers/")))')
L.append(' (net 0 "")')
for k,v in nets.items(): L.append(f' (net {k} "{v}")')
# outline (rounded rect) in KiCad coords
x0,x1,y0,y1=-W/2,W/2,-H/2,-YMIN   # KiCad y = -header y
segs=[((x0+RC,y0),(x1-RC,y0)),((x1,y0+RC),(x1,y1-RC)),((x1-RC,y1),(x0+RC,y1)),((x0,y1-RC),(x0,y0+RC))]
for a,b in segs: L.append(f' (gr_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (layer "Edge.Cuts") (width 0.15))')
for cx,cy,sx,sy in ((x0+RC,y0+RC,-1,-1),(x1-RC,y0+RC,1,-1),(x1-RC,y1-RC,1,1),(x0+RC,y1-RC,-1,1)):
    s=(cx+sx*RC,cy); m=(cx+sx*RC*math.cos(math.pi/4),cy+sy*RC*math.sin(math.pi/4)); e=(cx,cy+sy*RC)
    L.append(f' (gr_arc (start {s[0]:.4f} {s[1]:.4f}) (mid {m[0]:.4f} {m[1]:.4f}) (end {e[0]:.4f} {e[1]:.4f}) (layer "Edge.Cuts") (width 0.15))')
# footprint holding everything
F=[' (footprint "XL:AMPSEAL23_breakout" (layer "F.Cu") (at 0 0)',
   '  (fp_text reference "J1" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))',
   '  (fp_text value "AMPSEAL23" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))']
for n,x,y in pins:
    kx,ky=K(x,y)
    shape='rect' if n==1 else 'circle'
    F.append(f'  (pad "{n}" thru_hole {shape} (at {kx} {ky}) (size 2.3 2.3) (drill 1.6) (layers "*.Cu" "*.Mask") (net {n} "P{n}"))')
for x,y in pegs:
    kx,ky=K(x,y)
    F.append(f'  (pad "" np_thru_hole circle (at {kx} {ky}) (size 1.9 1.9) (drill 1.9) (layers "*.Cu" "*.Mask"))')
P=[]
for k,(n,xs,lay,px,py) in enumerate(tr):
    hx=XC-(NP-1)*PIT/2+k*PIT; hy=YI if k%2 else YO
    kx,ky=K(hx,hy)
    F.append(f'  (pad "{n}" smd roundrect (at {kx} {ky}) (size {PW} {PH}) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.2) (net {n} "P{n}"))')
    ty=hy+(1.0+PH/2+0.9 if k%2 else -(PH/2+0.9))   # inner row: number above pad; outer row: below (board edge)
    tkx,tky=K(hx,ty)
    F.append(f'  (fp_text user "{n}" (at {tkx} {tky}) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))')
    P.append((n,xs,lay,px,py,hx,hy))
F.append(' )')
L+=F
SEGS=[]
def seg(a,b,n,lay):
    ka,kb=K(*a),K(*b)
    L.append(f' (segment (start {ka[0]} {ka[1]}) (end {kb[0]} {kb[1]}) (width {TW}) (layer "{lay}") (net {n}))')
    SEGS.append((a,b,n,lay))
    if lay=='F.Cu':   # over-spec (Joel): F.Cu tracks left WITHOUT solder mask so they can be tinned thick with solder
        L.append(f' (gr_line (start {ka[0]} {ka[1]}) (end {kb[0]} {kb[1]}) (layer "F.Mask") (width {TW}))')
Y0=-6.0
for n,xs,lay,px,py,hx,hy in P:
    dx=hx-xs
    if lay=='F.Cu': pts=[(px,py),(xs,Y0)]
    else: pts=[(px,py),(px,-2.0),(xs,-2.0),(xs,Y0)]
    pts+= [(hx,Y0-abs(dx)),(hx,hy)]
    for a,b in zip(pts,pts[1:]):
        if a!=b: seg(a,b,n,lay)
    if lay=='B.Cu':
        kx,ky=K(hx,hy)
        L.append(f' (via (at {kx} {ky}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net {n}))')
L.append(')')
open(OUT,'w').write('\n'.join(L))
# clearance self-check (header coords): segments vs segments, segments vs pin/wire pads, same layer, different nets
def dps(p,a,b):
    ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L2)); return math.hypot(ax+t*dx-p[0],ay+t*dy-p[1])
def dss(a,b,c,d):
    return min(dps(a,c,d),dps(b,c,d),dps(c,a,b),dps(d,a,b)) if not inter(a,b,c,d) else 0
def inter(a,b,c,d):
    def o(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    return o(a,b,c)*o(a,b,d)<0 and o(c,d,a)*o(c,d,b)<0
m1=99; m2=99
for i,(a,b,n,l) in enumerate(SEGS):
    for (c,d,n2,l2) in SEGS[i+1:]:
        if l==l2 and n!=n2: m1=min(m1,dss(a,b,c,d)-TW)
    for nn,x,y in pins:
        if nn!=n: m2=min(m2,dps((x,y),a,b)-TW/2-1.15)
    for (nn,xs,ly,px,py,hx,hy) in P:
        if nn!=n and l=='F.Cu': m2=min(m2,dps((hx,hy),a,b)-TW/2-PW/2)   # square-ish pad approx
    for x,y in pegs: m2=min(m2,dps((x,y),a,b)-TW/2-0.95)
print('min seg-seg gap %.2f  min seg-pad gap %.2f (pads approximated as circles)'%(m1,m2))
print('edge order (header -x..+x):',[p[0] for p in P])
