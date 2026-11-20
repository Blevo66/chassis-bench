exec(open('tw3/helpers.py').read())
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
from OCP.collections import List_TopoDS_Shape
from OCP.TopAbs import TopAbs_FACE
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
OUT = 'tw3/out5/'
LEAN = np.radians(35); d = np.array([np.sin(LEAN), np.cos(LEAN)]); n = np.array([-np.cos(LEAN), np.sin(LEAN)])
LAMP_D, LAMP_L, LAMP_X, LAMP_Z, LAMP_F = 70.0, 60.0, 38.0, 153.0, 172.0
DC = np.array([95., 285.]); DH, DD, DW = 99., 53., 133.
BS0, BLEN, BW = DH / 2 + 10, 160., 240.
dash_a, dash_b = DC - d * DH / 2, DC + d * DH / 2
brd_a, brd_b = DC + d * BS0, DC + d * (BS0 + BLEN); BC = (brd_a + brd_b) / 2
def lean_f(z, off):  # f of the lean plane (through DC) at height z, offset 'off' along n (negative = into the body)
    p0 = DC + n * off; s_ = (z - p0[1]) / d[1]; return p0[0] + d[0] * s_
# side profile of the monocoque: (Z, rear f, front f, half width, squareness)
prof = [(90, 104, 150, 50, 2.6), (104, 86, 168, 72, 3.0), (125, 74, 180, 82, 3.4), (153, 68, 182, 84, 3.6), (185, 58, 180, 82, 3.4),
        (210, 52, 180, 77, 3.2), (235, lean_f(235, -6), 198, 74, 3.4), (275, lean_f(275, -6), 222, 74, 3.6), (320, lean_f(320, -6), 240, 76, 3.8),
        (370, lean_f(370, -6), 252, 82, 4.0), (420, lean_f(420, -6), 256, 88, 4.2), (455, lean_f(455, -6), 256, 90, 4.2), (470, lean_f(470, -6) + 8, 252, 84, 3.4)]
def sec(z, fr, ff, w, p, nn=96):
    th = np.linspace(0, 2 * np.pi, nn, endpoint=False); c, s_ = np.cos(th), np.sin(th)
    fc, a = (fr + ff) / 2, (ff - fr) / 2
    x = w * np.sign(c) * np.abs(c) ** (2 / p); f = fc + a * np.sign(s_) * np.abs(s_) ** (2 / p)
    return [W(ff_, z, xx) for xx, ff_ in zip(x, f)]
ts = BRepOffsetAPI_ThruSections(True, False, 1e-3)
for z, fr, ff, w, p in prof: ts.AddWire(spline_wire(sec(z, fr, ff, w, p)))
ts.CheckCompatibility(False); ts.Build(); body = ts.Shape()
# hollow: inner loft inset 3 mm, open at the bottom
T_SK = 3.0
ti = BRepOffsetAPI_ThruSections(True, False, 1e-3)
inner = [(prof[0][0] - 6,) + tuple(prof[0][1:])] + list(prof[1:-1]) + [(prof[-1][0] - T_SK,) + tuple(prof[-1][1:])]
for z, fr, ff, w, p in inner: ti.AddWire(spline_wire(sec(z, fr + T_SK, ff - T_SK, w - T_SK, p)))
ti.CheckCompatibility(False); ti.Build(); inner_s = ti.Shape()
from shapely.ops import unary_union
from shapely.geometry import Point
path = chaikin([(150, 212), (176, 252), (203, 300), (218, 350), (228, 405)], 3, closed=False)
rad = np.interp(np.linspace(0, 1, len(path)), [0, .35, 1], [21, 18, 12])
tun = unary_union([Point(p).buffer(r_, 32) for p, r_ in zip(path, rad)]).simplify(0.3)
TUN = side_part(tun, -150, 300); TUNW = side_part(tun.buffer(T_SK, 32), -150, 300)
shell = cut(cut(body, TUN), cut(inner_s, TUNW))
mono = shell if shell is not None else body
# lamp bores + dash pocket + side windows (through both side skins)
for s in (1, -1): mono = cut(mono, cyl(W(LAMP_F + 40, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 + 1, 80))
E2 = lambda v2: np.array([0, -v2[0], v2[1]])
def lean_poly(c2, poly_xy, b0, b1, axis_d, axis_n):
    o = W(*c2); pts = [o + np.array([x, 0, 0]) + E2(axis_d * y + axis_n * b0) for x, y in poly_xy]
    return prism(pts, E2(axis_n * (b1 - b0)))
rect = lambda w, h, r: ring(round_poly([(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)], r), 3)
mono = cut(mono, lean_poly(DC, rect(DW + 4, DH + 4, 11), -DD - 4, 30, d, n))
# neck (one piece with the shell)
arm = lambda s: [(s*37.5, 38), (s*43.5, 38), (s*43.5, -34), (s*36, -48), (s*22, -48), (s*22, -40), (s*37.5, -28)]
plan = SP(arm(1)).union(SP(arm(-1))).union(SP([(-36, -38), (36, -38), (36, -48), (-36, -48)]))
neck = prism([loc(v, u, 22) for v, u in ring(round_poly(plan, 3, 8), 3)], A * (115 - 22))
spine = round_poly([(-36, -38), (36, -38), (36, -48), (22, -60), (22, -150), (-22, -150), (-22, -60), (-36, -48)], 6, 10)
neck = fuse(neck, prism([loc(v, u, 55) for v, u in ring(spine, 3)], A * (160 - 55)))
for (u, t) in [(20, 35), (20, 100)]: neck = cut(neck, cyl(loc(-60, u, t), EX, 4.25, 120))
for s in (1, -1): neck = cut(neck, cyl(W(LAMP_F + 40, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 + 1, 140))
parts = {'monocoque_carbon': fuse(mono, neck)}
lamps = lens = None
for s in (1, -1):
    h = cyl(W(LAMP_F - 4, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2, LAMP_L); lamps = h if lamps is None else fuse(lamps, h)
    l = cyl(W(LAMP_F - 2, LAMP_Z, s * LAMP_X), (0, 1, 0), LAMP_D / 2 - 6, 2.5); lens = l if lens is None else fuse(lens, l)
parts['lamp_housings'] = lamps; parts['lamp_lenses'] = lens
parts['dash_pod_placeholder'] = lean_poly(DC, rect(DW, DH, 10), -DD, 0, d, n)
cb = lean_poly(BC, rect(BW, BLEN, 12), -4, 0, d, n)
for gx in range(-100, 101, 20):
    for gy in range(-60, 61, 20): cb = cut(cb, cyl(W(*(BC + d * gy - n * 10), gx), E2(n), 3.25, 20))
parts['cheeseboard_alu'] = cb
ins = None
for sx in (-50, 50):
    for sy in (-50, 50):
        i_ = cyl(W(*(BC + d * sy - n * 4), sx), E2(-n), 6, 10); ins = i_ if ins is None else fuse(ins, i_)
parts['m6_inserts_vesa100'] = ins
parts['tablet_tab_a9_placeholder'] = lean_poly(BC, rect(211, 125, 8), 12, 20, d, n)
vd = np.array([np.sin(np.radians(15)), np.cos(np.radians(15))]); vn = np.array([-vd[1], vd[0]])
vis = ring(SP(chaikin([(-104, 0), (104, 0), (84, 55), (30, 72), (-30, 72), (-84, 55)], 3)), 4)
parts['visor_polycarb'] = lean_poly(np.array([244, 466]), vis, -3, 0, vd, vn)
fx = None
for sgn in (1, -1):
    for (u, t) in [(20, 35), (20, 100)]:
        b_ = cyl(loc(sgn * 43.5, u, t), (sgn, 0, 0), 7.0, 4.0); fx = b_ if fx is None else fuse(fx, b_)
parts['button_heads_ti'] = fx
json.dump(dict(DC=DC.tolist(), BC=BC.tolist(), lean=35), open(OUT + 'layout.json', 'w'))
for k, s_ in parts.items():
    BRepMesh_IncrementalMesh(s_, 0.2, False, 0.25, True); w = StlAPI_Writer(); w.Write(s_, OUT + k + '.stl'); BRepTools.Write_s(s_, OUT + k + '.brep')
print(list(parts))
