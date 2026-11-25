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
up_mid={-12,-4,4,12}
top=[p for p in pins if p[2]==4.0 or (p[2]==0.0 and p[1] in up_mid)]
bot=[p for p in pins if p[2]==-4.0 or (p[2]==0.0 and p[1] not in up_mid)]
top.sort(key=lambda p:p[1]); bot.sort(key=lambda p:p[1])
PY=12.0; PW,PH=2.6,2.4   # wire pads 2.6 x 2.4 (drone-FC style), numbers printed outside them
def padx(n,i,p): return -((n-1)*p)/2+i*p
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
# outline (rounded rect) in KiCad coords, centred on 0,0 (symmetric so mirroring is irrelevant)
x0,x1,y0,y1=-W/2,W/2,-H/2,H/2
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
def addpads(lst,ysign,pitch):
    out=[]
    for i,(n,x,y) in enumerate(lst):
        hx=padx(len(lst),i,pitch); hy=ysign*PY
        kx,ky=K(hx,hy)
        F.append(f'  (pad "{n}" smd roundrect (at {kx} {ky}) (size {PW} {PH}) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.2) (net {n} "P{n}"))')
        ty=hy+ysign*(PH/2+1.4)    # number between pad and board edge
        tkx,tky=K(hx,ty)
        F.append(f'  (fp_text user "{n}" (at {tkx} {tky}) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.2))))')
        out.append((n,x,y,hx,hy))
    return out
T=addpads(top,1,3.2); B=addpads(bot,-1,3.2)   # tight pitch keeps the fan-out short and well clear of the peg holes
F.append(' )')
L+=F
def seg(a,b,n):
    ka,kb=K(*a),K(*b)
    L.append(f' (segment (start {ka[0]} {ka[1]}) (end {kb[0]} {kb[1]}) (width {TW}) (layer "F.Cu") (net {n}))')
for lst,s in ((T,1),(B,-1)):
    for n,x,y,hx,hy in lst:
        ye=s*7.0          # leave the pin field
        yb=s*9.6
        pts=[(x,y),(x,ye),(hx,yb),(hx,hy)]
        for a,b in zip(pts,pts[1:]):
            if a!=b: seg(a,b,n)
L.append(')')
open(OUT,'w').write('\n'.join(L))
# quick clearance self-check between different-net copper on F.Cu (segments vs pads vs segments)
print('pads top',[t[0] for t in T]); print('pads bottom',[b[0] for b in B])
