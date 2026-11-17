"""Rear side tanks: a faceted pod each side, outboard of the rear frame rails.
Rings at X stations (mm from swingarm pivot, X fwd, Y left, Z up). Each ring: inner top (seam), outer top,
outer belly, outer bottom, inner bottom. Inner face flat (against the rail clamps), bottom flat.
Usage: python3 rear.py OUTDIR"""
import sys, os, json, numpy as np, trimesh, ezdxf, shapely.geometry as sg, shapely.ops as so
from shapely import affinity
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'twin-saddle'))
import tri
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); T = 1.2
#        x     yi   zt   yo-top zt-out  yo   zm   yo-bot  zb
ST = [(-110, 147, 296, 196, 288, 232, 262, 214, 232),
      (-200, 147, 318, 214, 312, 246, 268, 226, 228),
      (-290, 150, 338, 206, 330, 238, 292, 220, 242),
      (-350, 152, 350, 186, 344, 204, 322, 194, 284)]
ENDS = ((-80, 0.42), (-380, 0.40))          # chamfered ends: small flat end faces
def ring(s):
    x, yi, zt, yot, zto, yo, zm, yob, zb = s
    return np.array([[x, yi, zt], [x, yot, zto], [x, yo, zm], [x, yob, zb], [x, yi, zb]], float)
R = [ring(s) for s in ST]
def endring(Rr, x, k):
    c = Rr.mean(0); E = c + (Rr - c) * k; E[:, 0] = x; return E
rings = [endring(R[0], *ENDS[0])] + R + [endring(R[-1], *ENDS[1])]
rings = rings[::-1]                           # rear to front
N = 5; V = np.vstack(rings); idx = lambda r, i: r * N + (i % N)
panels = []
for r in range(len(rings) - 1):
    band = []
    for i in range(N):
        band += [(idx(r, i), idx(r + 1, i), idx(r + 1, i + 1)), (idx(r, i), idx(r + 1, i + 1), idx(r, i + 1))]
    panels.append((f'strip-{r+1}', band))
faces = [f for _, b in panels for f in b]
caps = [[idx(0, i) for i in range(N)], [idx(len(rings) - 1, i) for i in range(N)]]
capt = [(c[0], c[i], c[i + 1]) for c in caps for i in range(1, N - 1)]
def mesh(side):
    Vs = V.copy(); Vs[:, 1] *= side
    m = trimesh.Trimesh(Vs, faces + capt, process=False); m.fix_normals(); return m
L = mesh(1); Rm = mesh(-1)
info = {'version': 'rear side tanks v1', 'litres_each': round(L.volume / 1e6, 2), 'litres_pair': round(2 * L.volume / 1e6, 2),
        'bounds_left': L.bounds.round().tolist(), 'parts': {}}
# fold edge lengths
fl = []
for _, b in panels:
    for k in range(1, len(b)):
        sh = [v for v in b[k] if v in b[k - 1]]; fl.append(np.linalg.norm(V[sh[0]] - V[sh[1]]))
info['longest_fold_line_mm'] = round(max(fl), 1)
# outward normals from the closed mesh, to label folds out / IN
fn = {tuple(sorted(f)): n for f, n in zip(L.faces.tolist(), L.face_normals)}
def kind(f1, f2, sh):
    n = fn[tuple(sorted(f1))]; o = [v for v in f2 if v not in sh][0]
    return 'out' if np.dot(V[o] - V[sh[0]], n) < 0 else 'IN'
def save(name, poly, folds=(), note=''):
    doc = ezdxf.new('R2010'); msp = doc.modelspace()
    for l, c in (('CUT', 1), ('ETCH_FOLD', 5), ('NOTE', 3)): doc.layers.add(l, color=c)
    msp.add_lwpolyline(list(poly.exterior.coords), close=True, dxfattribs={'layer': 'CUT'})
    for a, b, ang, kd in folds:
        if ang < 3: continue
        msp.add_line(tuple(a), tuple(b), dxfattribs={'layer': 'ETCH_FOLD'})
        mm = (a + b) / 2; msp.add_text(f'{ang:.0f} {kd}', dxfattribs={'layer': 'NOTE', 'height': 5}).set_placement(tuple(mm))
    x0, y0, _, _ = poly.bounds
    msp.add_text(f'REAR TANK {name} - LEFT (mirror for RIGHT) - {T} mm mild steel - {note}', dxfattribs={'layer': 'NOTE', 'height': 7}).set_placement((x0, y0 - 15))
    doc.saveas(f'{OUT}/rear-flat-{name}.dxf')
flats = {}; area = 0
for name, band in panels:
    t2, folds = tri.unfold_band(V, band)
    ps = [sg.Polygon(t) for t in t2]
    u = so.unary_union([p.buffer(0.05, join_style=2) for p in ps]).buffer(-0.05, join_style=2)
    if u.geom_type != 'Polygon': u = max(u.geoms, key=lambda g: g.area)
    ov = sum(p.area for p in ps) - u.area
    fk = [(folds[k - 1][0], folds[k - 1][1], folds[k - 1][2], kind(band[k - 1], band[k], [v for v in band[k] if v in band[k - 1]])) for k in range(1, len(band))]
    mrr = np.array(u.minimum_rotated_rectangle.exterior.coords)[:4]
    e = mrr[1] - mrr[0] if np.linalg.norm(mrr[1] - mrr[0]) > np.linalg.norm(mrr[2] - mrr[1]) else mrr[2] - mrr[1]
    a = -np.arctan2(e[1], e[0]); Rt = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    u = affinity.rotate(u, a, origin=(0, 0), use_radians=True); fk = [(Rt @ p, Rt @ q, an, kd) for p, q, an, kd in fk]
    save(name, u, fk, 'ring strip, closes on itself at the inner top edge'); flats[name] = (u, fk); area += u.area
    info['parts'][name] = {'flat_mm': [round(u.bounds[2] - u.bounds[0]), round(u.bounds[3] - u.bounds[1])],
                           'real_folds': sum(1 for f in fk if f[2] >= 3), 'overlap_mm2': round(ov, 1)}
for nm, c in (('end-rear', caps[0]), ('end-front', caps[1])):
    p = sg.Polygon(V[c][:, 1:]); p = affinity.translate(p, -p.centroid.x, -p.centroid.y)
    save(nm, p, note='flat end face'); flats[nm] = (p, []); area += p.area
    info['parts'][nm] = {'flat_mm': [round(p.bounds[2] - p.bounds[0]), round(p.bounds[3] - p.bounds[1])]}
info['steel_kg_each'] = round(area * T * 7.85e-6, 2)
info['lowest_point_z'] = round(float(V[:, 2].min()))
info['stations'] = ST
L.export(f'{OUT}/rear-tank-left.stl'); Rm.export(f'{OUT}/rear-tank-right.stl')
for nm, mm in (('left', L), ('right', Rm)):          # 2 pieces each for the Bambu bed
    for part, n in (('front', [1, 0, 0]), ('rear', [-1, 0, 0])):
        q = mm.slice_plane([-230, 0, 0], n, cap=True); q.apply_translation(-q.bounds[0])
        q.export(f'{OUT}/mockup-rear-tank-{nm}-{part}.stl'); info.setdefault('mockup_sizes_mm', {})[f'{nm}-{part}'] = [round(v) for v in q.extents]
fr = trimesh.load('/mnt/project-files/frame-scan/fusion/xl125r-frame-scan-full.stl')
pts = fr.vertices[(fr.vertices[:, 0] < -40) & (fr.vertices[:, 0] > -420)]
for nm, mm in (('left', L), ('right', Rm)):
    d = trimesh.proximity.ProximityQuery(mm).signed_distance(pts)
    info.setdefault('clearance_to_scan_mm', {})[nm] = round(float(-d.max()), 1)
import pickle; pickle.dump(flats, open(f'{OUT}/.rflats.pkl', 'wb'))
json.dump(info, open(f'{OUT}/rear-tank-info.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in info.items() if k != 'stations'}, indent=0))
