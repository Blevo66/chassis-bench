import sys, json; sys.path.insert(0, 'tw3'); from common import *
from shapely.geometry import Polygon as SP, box as sbox
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
P3 = lambda p: gp_Pnt(*map(float, p))
def prism(pts3, vec):
    mp = BRepBuilderAPI_MakePolygon()
    for p in pts3: mp.Add(P3(p))
    mp.Close(); f = BRepBuilderAPI_MakeFace(mp.Wire()).Face()
    return BRepPrimAPI_MakePrism(f, gp_Vec(*map(float, vec))).Shape()
def cyl(c, axis, r, h):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(P3(c), gp_Dir(*axis)), float(r), float(h)).Shape()
def cut(a, b): return BRepAlgoAPI_Cut(a, b).Shape()
def fuse(a, b): return BRepAlgoAPI_Fuse(a, b).Shape()
def fillet(s, r):
    try:
        mk = BRepFilletAPI_MakeFillet(s); ex = TopExp_Explorer(s, TopAbs_EDGE)
        while ex.More(): mk.Add(float(r), TopoDS.Edge_s(ex.Current())); ex.Next()
        mk.Build(); return mk.Shape() if mk.IsDone() else s
    except Exception: return s
W = lambda f, z, x=0.0: np.array([x, -f, z], float)            # side (fwd, Z) -> world
def side_part(prof, x0, dx): return prism([W(f, z, x0) for f, z in prof], (dx, 0, 0))
def loc(v, u, t): return v * EX + u * B + t * A                 # steering-local -> world
# ---------------- parameters
LEAN = np.radians(35); d = np.array([np.sin(LEAN), np.cos(LEAN)]); n = np.array([-np.cos(LEAN), np.sin(LEAN)])
CH_IN, CH_T = 99.0, 4.0                       # cheek inner face |X|, thickness
LAMP_D, LAMP_L, LAMP_X, LAMP_Z, LAMP_F = 90.0, 60.0, 52.0, 155.0, 162.0   # housing dia, depth, centres, lens front f
DC = np.array([95., 285.]); DH, DD, DW = 99., 53., 133.
BS0, BLEN, BW, BT = DH / 2 + 10, 160., 240., 4.
dash_a, dash_b = DC - d * DH / 2, DC + d * DH / 2
brd_a, brd_b = DC + d * BS0, DC + d * (BS0 + BLEN); BC = (brd_a + brd_b) / 2
BULK = [(84., 98.), (52., 205.)]; BULK_T = 5.0
POD_Z0, POD_Z1, POD_FRONT = 98.0, 206.0, 150.0
parts = {}
# ---------------- neck (steering-local, bolted to the 4 bosses), outer moulded shape
arm = lambda s: [(s*37.5, 38), (s*43.5, 38), (s*43.5, -36), (s*36, -48), (s*30, -48), (s*30, -38), (s*37.5, -30)]
neck = None
for s in (1, -1):
    pa = [tuple(p) for p in arm(s)]; pa = pa if s > 0 else pa[::-1]
    a_ = prism([loc(v, u, 22) for v, u in pa], A * (115 - 22)); neck = a_ if neck is None else fuse(neck, a_)
bar = [(-36, -38), (36, -38), (36, -48), (22, -48), (22, -140), (-22, -140), (-22, -48), (-36, -48)]
neck = fuse(neck, prism([loc(v, u, 55) for v, u in bar], A * (160 - 55)))
for (u, t) in [(20, 35), (20, 100)]:
    neck = cut(neck, cyl(loc(-60, u, t), EX, 4.25, 120))           # M8 clearance at the bosses
parts['neck_carbon'] = neck
# ---------------- body side profile (fwd, Z)
cheek_prof = [(BULK[0][0] - BULK_T, BULK[0][1]), (100, 84), (176, 90), (POD_FRONT + 20, POD_Z0 + 8), (POD_FRONT + 4, POD_Z1),
              tuple(brd_b - n * 10), tuple(brd_a - n * 10), tuple(dash_b + n * 6), tuple(dash_a + n * 6),
              (BULK[1][0] - BULK_T, BULK[1][1] + 6)]
cp = SP(cheek_prof)
core = cp.buffer(-17, join_style=2)
lam = SP([(0, POD_Z1 + 22), (400, POD_Z1 + 22), (400, 700), (0, 700)])
cradle_zone = SP([tuple(brd_a - n * 30 - d * 50), tuple(brd_b - n * 30 + d * 50), tuple(brd_b + n * 200), tuple(brd_a + n * 200)])
win = core.intersection(lam).difference(cradle_zone)
web = SP([tuple(dash_b - n * 40 + d * 0), tuple(dash_b - n * 40 + d * 14), tuple(brd_b - n * 140 + d * 30), tuple(brd_b - n * 140 + d * 16)]).buffer(0)
web = SP([(150, 230), (164, 230), (205, 420), (191, 420)])
win = win.difference(web.buffer(6))
wins = [g for g in (win.geoms if hasattr(win, 'geoms') else [win]) if g.area > 400]
wins = [w.buffer(-6).buffer(6) for w in wins]
for s in (1, -1):
    x0 = s * CH_IN if s > 0 else -CH_IN - CH_T
    c = side_part(cheek_prof, x0, CH_T)
    for w in wins:
        pts = list(w.exterior.coords)[:-1]; c = cut(c, side_part(pts, x0 - 1, CH_T + 2))
    parts[f'cheek_{"R" if s > 0 else "L"}'] = c
# bulkhead (slanted plate across, clear of the sweep), pod floor, pod front with lamp holes
f0, z0 = BULK[0]; f1, z1 = BULK[1]; tdir = np.array([f1 - f0, z1 - z0]); tdir /= np.linalg.norm(tdir); nb = np.array([-tdir[1], tdir[0]]) * -1
bulk_prof = [(f0, z0), (f1, z1), tuple(np.array([f1, z1]) - np.array([BULK_T, 0])), (f0 - BULK_T, z0)]
parts['bulkhead'] = side_part(bulk_prof, -CH_IN, 2 * CH_IN)
_pf = side_part([(BULK[0][0] - 2, POD_Z0), (POD_FRONT + 13, POD_Z0), (POD_FRONT + 13, POD_Z0 + 4), (BULK[0][0] - 3, POD_Z0 + 4)], -CH_IN, 2 * CH_IN)
front = side_part([(POD_FRONT + 16, POD_Z0 + 8), (POD_FRONT + 20, POD_Z0 + 8), (POD_FRONT + 4, POD_Z1), (POD_FRONT, POD_Z1)], -CH_IN, 2 * CH_IN)
for s in (1, -1): front = cut(front, cyl(W(POD_FRONT + 40, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 + 1.5, 60))
parts['pod_front'] = front
parts['pod_top'] = side_part([(POD_FRONT, POD_Z1), (POD_FRONT + 13, POD_Z1), tuple(dash_a - n * DD + d * 0 + np.array([0, -3])), tuple(dash_a - n * DD + np.array([-4, 0]))], -CH_IN, 2 * CH_IN) if False else None
del parts['pod_top']
# chin: front lip under the lamps, sloped
parts['chin'] = side_part([(100, 84), (176, 90), (POD_FRONT + 20, POD_Z0 + 8), (BULK[0][0] - 2, POD_Z0 + 4), (BULK[0][0] - 4, POD_Z0)], -CH_IN, 2 * CH_IN)
# lamps
lamps = None; lens = None
for s in (1, -1):
    h = cyl(W(LAMP_F - 3, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2, LAMP_L - 3); lamps = h if lamps is None else fuse(lamps, h)
    l = cyl(W(LAMP_F, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 - 5, 3); lens = l if lens is None else fuse(lens, l)
parts['lamp_housings'] = lamps; parts['lamp_lenses'] = lens
# dash pod placeholder + folded alu bracket
E2 = lambda v2: np.array([0, -v2[0], v2[1]])   # side vector -> world
def lean_plate(c2, a0, a1, b0, b1, x0, x1, axis_d, axis_n):
    """plate spanning x0..x1 laterally, along side vector axis_d from a0..a1, thickness along axis_n b0..b1, origin c2 (side)"""
    o = W(*c2); pts = [o + E2(axis_d * a0 + axis_n * b0), o + E2(axis_d * a1 + axis_n * b0), o + E2(axis_d * a1 + axis_n * b1), o + E2(axis_d * a0 + axis_n * b1)]
    return prism([p + np.array([x0, 0, 0]) for p in pts], (x1 - x0, 0, 0))
parts['dash_pod_placeholder'] = lean_plate(DC, -DH / 2, DH / 2, -DD, 0, -DW / 2, DW / 2, d, n)
parts['dash_bracket_alu'] = lean_plate(DC, -DH / 2 - 6, DH / 2 + 6, -DD - 3, -DD, -CH_IN, CH_IN, d, n)
# forged-carbon top cradle with VESA-100 M6 inserts
cr = lean_plate(BC, -BLEN / 2, BLEN / 2, -10, -4, -CH_IN - CH_T, CH_IN + CH_T, d, n)
for sx in (-50, 50):
    for sy in (-50, 50):
        cr = cut(cr, cyl(W(*(BC + d * sy - n * 20), sx), E2(n), 3.0, 40))
parts['top_cradle_forged'] = cr
# cheeseboard 240x160x4 alu, 6.5 holes on 20 grid
cb = lean_plate(BC, -BLEN / 2, BLEN / 2, -4, 0, -BW / 2, BW / 2, d, n)
for gx in range(-100, 101, 20):
    for gy in range(-60, 61, 20):
        cb = cut(cb, cyl(W(*(BC + d * gy - n * 10), gx), E2(n), 3.25, 20))
parts['cheeseboard_alu'] = cb
parts['tablet_tab_a9_placeholder'] = lean_plate(BC, -62.5, 62.5, 12, 20, -105.5, 105.5, d, n)
# visor (smoked polycarbonate) off the front edge of the cradle
vd = np.array([np.sin(np.radians(15)), np.cos(np.radians(15))]); vn = np.array([-vd[1], vd[0]])
vo = brd_b - n * 4
parts['visor_polycarb'] = lean_plate(vo, 0, 60, -3, 0, -100, 100, vd, vn)
fx = None
def addbolt(c3, axis, r=5.0, h=2.5):
    global fx; b = cyl(c3, axis, r, h); fx = b if fx is None else fuse(fx, b)
for sgn in (1, -1):
    xo = sgn * (CH_IN + CH_T); ax_ = (sgn, 0, 0)
    for f_, z_ in [(BULK[0][0] + 8, 108), (POD_FRONT + 4, POD_Z0 + 18), (POD_FRONT - 6, POD_Z1 - 10), (BULK[1][0] + 4, BULK[1][1] - 10),
                   tuple(DC - d * 40 - n * (DD + 1.5)), tuple(DC + d * 40 - n * (DD + 1.5)), tuple(brd_a - n * 7 + d * 15), tuple(brd_b - n * 7 - d * 15)]:
        addbolt(W(f_, z_, xo), ax_)
    for (u, t) in [(20, 35), (20, 100)]: addbolt(loc(sgn * 43.5, u, t), ax_, 7.0, 4.0)
parts['button_heads_ti'] = fx
# ---------------- export
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
json.dump(dict(DC=DC.tolist(), BC=BC.tolist(), brd_a=brd_a.tolist(), brd_b=brd_b.tolist(), dash_a=dash_a.tolist(), dash_b=dash_b.tolist(), lean=35), open('tw3/out/layout.json', 'w'))
for k, s in parts.items():
    BRepMesh_IncrementalMesh(s, 0.3, False, 0.3, True); w = StlAPI_Writer(); w.Write(s, f'tw3/out/{k}.stl')
import pickle
from OCP.BRepTools import BRepTools
for k, s in parts.items(): BRepTools.Write_s(s, f'tw3/out/{k}.brep')
print('parts', list(parts))
