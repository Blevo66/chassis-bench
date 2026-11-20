import sys, json; sys.path.insert(0, 'tw3'); from common import *
from shapely.geometry import Polygon as SP, LineString
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepTools import BRepTools
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt
P3 = lambda p: gp_Pnt(*map(float, p))
def chaikin(P, n=4, closed=True):
    P = np.asarray(P, float)
    for _ in range(n):
        Q = []
        for i in range(len(P) if closed else len(P) - 1):
            a, b = P[i], P[(i + 1) % len(P)]; Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        P = np.array(Q)
    return P
def spline_wire(pts3):
    arr = TColgp_HArray1OfPnt(1, len(pts3))
    for i, p in enumerate(pts3): arr.SetValue(i + 1, P3(p))
    it = GeomAPI_Interpolate(arr, True, 1e-6); it.Perform()
    return BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(it.Curve()).Edge()).Wire()
def prism(pts3, vec, smooth=False):
    if smooth: w = spline_wire(pts3)
    else:
        mp = BRepBuilderAPI_MakePolygon()
        for p in pts3: mp.Add(P3(p))
        mp.Close(); w = mp.Wire()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w).Face(), gp_Vec(*map(float, vec))).Shape()
def cyl(c, axis, r, h):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(P3(c), gp_Dir(*axis)), float(r), float(h)).Shape()
cut = lambda a, b: BRepAlgoAPI_Cut(a, b).Shape(); fuse = lambda a, b: BRepAlgoAPI_Fuse(a, b).Shape()
def fillet(s, r):
    try:
        mk = BRepFilletAPI_MakeFillet(s); ex = TopExp_Explorer(s, TopAbs_EDGE)
        while ex.More(): mk.Add(float(r), TopoDS.Edge(ex.Current())); ex.Next()
        mk.Build()
        return mk.Shape() if mk.IsDone() else s
    except Exception as e: print('fillet failed', e); return s
W = lambda f, z, x=0.0: np.array([x, -f, z], float)
loc = lambda v, u, t: v * EX + u * B + t * A
def round_poly(p, r_out, r_in=None):
    p = SP(p).buffer(0); p = p.buffer(-r_out, join_style=1).buffer(r_out, join_style=1)
    if r_in: p = p.buffer(r_in, join_style=1).buffer(-r_in, join_style=1)
    return p
def ring(poly, step=4.0):
    c = np.array(poly.exterior.coords)[:-1]; L = LineString(np.vstack([c, c[:1]]))
    k = max(24, int(L.length / step)); return np.array([L.interpolate(i / k, normalized=True).coords[0] for i in range(k)])
def side_part(poly2, x0, dx, smooth=True):
    pts = ring(poly2, 6.0) if smooth else np.asarray(poly2)
    return prism([W(f, z, x0) for f, z in pts], (dx, 0, 0), smooth=False)
# ---------------- parameters
LEAN = np.radians(35); d = np.array([np.sin(LEAN), np.cos(LEAN)]); n = np.array([-np.cos(LEAN), np.sin(LEAN)])
CH_IN, CH_T = 95.0, 12.0
LAMP_D, LAMP_L, LAMP_X, LAMP_Z, LAMP_F = 85.0, 60.0, 46.0, 153.0, 166.0
DC = np.array([95., 285.]); DH, DD, DW = 99., 53., 133.
BS0, BLEN, BW = DH / 2 + 10, 160., 240.
dash_a, dash_b = DC - d * DH / 2, DC + d * DH / 2
brd_a, brd_b = DC + d * BS0, DC + d * (BS0 + BLEN); BC = (brd_a + brd_b) / 2
parts = {}
# ---------------- neck, rounded in plan
for s in (1, -1):
    pass
arm = lambda s: [(s*37.5, 38), (s*43.5, 38), (s*43.5, -34), (s*36, -48), (s*22, -48), (s*22, -40), (s*37.5, -28)]
plan = SP(arm(1)).union(SP(arm(-1))).union(SP([(-36, -38), (36, -38), (36, -48), (-36, -48)]))
plan_r = round_poly(plan, 3, 8)
neck = prism([loc(v, u, 22) for v, u in ring(plan_r, 3)], A * (115 - 22))
spine = round_poly([(-22, -40), (22, -40), (22, -140), (-22, -140)], 8)
neck = fuse(neck, prism([loc(v, u, 55) for v, u in ring(spine, 3)], A * (160 - 55)))
neck = fuse(neck, prism([loc(v, u, 55) for v, u in ring(round_poly([(-36, -38), (36, -38), (36, -48), (-36, -48)], 3), 3)], A * (160 - 55)))
for (u, t) in [(20, 35), (20, 100)]: neck = cut(neck, cyl(loc(-60, u, t), EX, 4.25, 120))
parts['neck_carbon'] = neck
# ---------------- organic nose: loft of superellipse sections along the lamp axis
def superellipse(zc, a, b, p, f, nn=72, droop=0.0):
    th = np.linspace(0, 2*np.pi, nn, endpoint=False); c, s_ = np.cos(th), np.sin(th)
    x = a * np.sign(c) * np.abs(c) ** (2 / p); z = b * np.sign(s_) * np.abs(s_) ** (2 / p)
    z = z - droop * np.clip(-s_, 0, 1) ** 3 * (1 - np.abs(c))      # beak: pull the bottom-centre down
    return [W(f, zc + zz, xx) for xx, zz in zip(x, z)]
secs = [(84, 152, 90, 56, 3.2, 0), (112, 153, 94, 60, 3.4, 10), (142, 153, 93, 58, 3.3, 16), (162, 152, 88, 52, 3.0, 12), (172, 151, 78, 45, 2.6, 6)]
ts = BRepOffsetAPI_ThruSections(True, False, 1e-3)
for f, zc, a, b, p, dr in secs: ts.AddWire(spline_wire(superellipse(zc, a, b, p, f, droop=dr)))
ts.Build(); nose = ts.Shape()
for s in (1, -1): nose = cut(nose, cyl(W(LAMP_F + 30, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 + 1.0, 100))
nose = cut(nose, cyl(W(LAMP_F + 30, LAMP_Z, 0), (0, 1, 0), 1, 1)) if False else nose
parts['nose_cowl'] = nose
# lamps (housing + lens + chrome-ish bezel)
lamps = lens = bez = None
for s in (1, -1):
    h = cyl(W(LAMP_F - 2, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2, LAMP_L); lamps = h if lamps is None else fuse(lamps, h)
    l = cyl(W(LAMP_F, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 - 6, 2.5); lens = l if lens is None else fuse(lens, l)
parts['lamp_housings'] = lamps; parts['lamp_lenses'] = lens
# ---------------- cheeks: flowing outline
cheek = [(80, 104), (120, 92), (165, 112), (178, 160), (176, 215), tuple(brd_b - n * 10 + d * 6), tuple(brd_b - n * 4 + d * 2),
         tuple(brd_a - n * 4 - d * 4), tuple(dash_b + n * 4), tuple(dash_a + n * 10), (45, 215), (62, 150)]
cheek_s = SP(chaikin(cheek, 4)).buffer(0)
core = cheek_s.buffer(-16, join_style=1)
nose_zone = SP([(0, 0), (400, 0), (400, 112), (0, 112)])
cradle_zone = SP([tuple(brd_a - n * 22 - d * 80), tuple(brd_b - n * 22 + d * 80), tuple(brd_b + n * 200), tuple(brd_a + n * 200)])
win = core.difference(nose_zone).difference(cradle_zone)
web = (LineString(chaikin([(40, 205), (110, 222), (190, 200)], 3, closed=False)).buffer(11))
win = win.difference(web)
wins = [g.buffer(-8, join_style=1).buffer(8, join_style=1) for g in (win.geoms if hasattr(win, 'geoms') else [win])]
wins = [w for w in wins if w.area > 500]
for s in (1, -1):
    x0 = CH_IN if s > 0 else -CH_IN - CH_T
    c = side_part(cheek_s, x0, CH_T)
    for w in wins: c = cut(c, side_part(w, x0 - 1, CH_T + 2))
    parts[f'cheek_{"R" if s > 0 else "L"}'] = fillet(c, 4.0)
# bulkhead behind nose / under dash (hidden structure, sweep-clear line)
BULK = [(84., 110.), (52., 210.)]
parts['bulkhead'] = side_part([(84, 110), (52, 210), (47, 210), (79, 110)], -CH_IN, 2 * CH_IN, smooth=False)
# dash + bracket
E2 = lambda v2: np.array([0, -v2[0], v2[1]])
def lean_poly(c2, poly_xy, b0, b1, axis_d, axis_n):
    o = W(*c2); pts = [o + np.array([x, 0, 0]) + E2(axis_d * y + axis_n * b0) for x, y in poly_xy]
    return prism(pts, E2(axis_n * (b1 - b0)))
rect = lambda w, h, r: ring(round_poly([(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)], r), 3)
parts['dash_pod_placeholder'] = lean_poly(DC, rect(DW, DH, 10), -DD, 0, d, n)
parts['dash_bracket_alu'] = lean_poly(DC, rect(2 * CH_IN, DH + 12, 8), -DD - 3, -DD, d, n)
# cradle: organic forged plate, shield-shaped
cr_outline = ring(SP(chaikin([(-CH_IN - CH_T, -BLEN/2 - 6), (CH_IN + CH_T, -BLEN/2 - 6), (CH_IN + 14, BLEN/2 + 2), (60, BLEN/2 + 14), (-60, BLEN/2 + 14), (-CH_IN - 14, BLEN/2 + 2)], 3)), 4)
cr = lean_poly(BC, cr_outline, -10, -4, d, n)
for sx in (-50, 50):
    for sy in (-50, 50): cr = cut(cr, cyl(W(*(BC + d * sy - n * 20), sx), E2(n), 3.0, 40))
parts['top_cradle_forged'] = fillet(cr, 1.5)
cb = lean_poly(BC, rect(BW, BLEN, 12), -4, 0, d, n)
for gx in range(-100, 101, 20):
    for gy in range(-60, 61, 20): cb = cut(cb, cyl(W(*(BC + d * gy - n * 10), gx), E2(n), 3.25, 20))
parts['cheeseboard_alu'] = cb
parts['tablet_tab_a9_placeholder'] = lean_poly(BC, rect(211, 125, 8), 12, 20, d, n)
vd = np.array([np.sin(np.radians(15)), np.cos(np.radians(15))]); vn = np.array([-vd[1], vd[0]])
vis = ring(SP(chaikin([(-100, 0), (100, 0), (80, 55), (30, 72), (-30, 72), (-80, 55)], 3)), 4)
parts['visor_polycarb'] = lean_poly(brd_b - n * 4 + d * 8, vis, -3, 0, vd, vn)
# bolts
fx = None
def addbolt(c3, axis, r=5.0, h=2.5):
    global fx; b = cyl(c3, axis, r, h); fx = b if fx is None else fuse(fx, b)
for sgn in (1, -1):
    xo = sgn * (CH_IN + CH_T); ax_ = (sgn, 0, 0)
    for f_, z_ in [(70, 235), tuple(DC - d * 40 - n * (DD + 1.5)), tuple(DC + d * 40 - n * (DD + 1.5)), tuple(brd_a - n * 7 + d * 15), tuple(brd_b - n * 7 - d * 15)]:
        addbolt(W(f_, z_, xo), ax_)
    for (u, t) in [(20, 35), (20, 100)]: addbolt(loc(sgn * 43.5, u, t), ax_, 7.0, 4.0)
parts['button_heads_ti'] = fx
json.dump(dict(DC=DC.tolist(), BC=BC.tolist(), lean=35), open('tw3/out3/layout.json', 'w'))
for k, s in parts.items():
    BRepMesh_IncrementalMesh(s, 0.2, False, 0.25, True); w = StlAPI_Writer(); w.Write(s, f'tw3/out3/{k}.stl'); BRepTools.Write_s(s, f'tw3/out3/{k}.brep')
print(list(parts))
