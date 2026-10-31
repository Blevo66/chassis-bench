"""Turn the topology-optimised density into a smooth outline, check clearance, and export DXF / STL / 3MF / picture."""
import json, math, numpy as np
from skimage import measure
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import design as DS
from design import smooth_outline, rounded_slab, cs, m3, poses, arm_band, arm_to_world, shock_end
g = json.load(open('topopt_grid.json')); rho = np.load('topopt_density.npy')
H = g['H']
pad = np.pad(rho, 1)
polys = []
for c in measure.find_contours(pad, 0.5):
    xy = np.c_[g['minx'] + (c[:, 0] - 1 + .5)*H, g['miny'] + (c[:, 1] - 1 + .5)*H]
    if len(xy) > 10: polys.append(Polygon(xy).buffer(0))
# outer shapes minus inner holes: use even-odd by symmetric difference
shape = None
for p in sorted(polys, key=lambda p: -p.area):
    shape = p if shape is None else shape.symmetric_difference(p)
HR = DS.HOLE/2
bosses = unary_union([Point(*c).buffer(HR + 6.0, 64) for c in ((0, 0), tuple(DS.Dl), tuple(DS.Sl))])
shape = unary_union([shape.buffer(0), bosses])
if isinstance(shape, MultiPolygon): shape = max(shape.geoms, key=lambda q: q.area)
# smooth outer and inner edges; drop slivers and tiny holes
shape = shape.buffer(-1.0, 64).buffer(1.0, 64)
outer = smooth_outline(Polygon(shape.exterior), 2.0)
inner = [smooth_outline(Polygon(r), 2.0) for r in shape.interiors if Polygon(r).area > 40]
body = unary_union([outer.difference(unary_union(inner)) if inner else outer, bosses])
if isinstance(body, MultiPolygon): body = max(body.geoms, key=lambda q: q.area)
# clearance re-check against the real arm slice and the shock body (keep-outs were in the design space already)
gaps = []
for p in poses:
    rk = affinity.translate(affinity.rotate(body, p['rang'], origin=(0, 0), use_radians=True), *p['R'])
    a = unary_union([arm_to_world(x, p['th']) for x in arm_band])
    gaps.append((rk.distance(a), rk.distance(shock_end(p)), p['th']/D2R if False else p['th']*180/math.pi))
ga = min(gaps, key=lambda t: t[0]); gs = min(gaps, key=lambda t: t[1])
print(f'gap to arm {ga[0]:.1f} mm (arm {ga[2]:.1f} deg), gap to shock body {gs[1]:.1f} mm, area {body.area:.0f} mm2, windows {len(body.interiors)}')
holes = unary_union([Point(*c).buffer(HR, 64) for c in ((0, 0), tuple(DS.Dl), tuple(DS.Sl))])
part2d = body.difference(holes)
# --- DXF in Joel's sketch frame: right-side view, full droop, pivot hole at 0,0, mm
p0 = poses[0]
def to_sketch(geom):
    geom = affinity.rotate(geom, p0['rang'], origin=(0, 0), use_radians=True)
    return affinity.scale(geom, -1, 1, origin=(0, 0))
sk = to_sketch(part2d)
def dxf_poly(pts):
    s = '0\nPOLYLINE\n8\nROCKER\n66\n1\n70\n1\n'
    for x, y in pts: s += f'0\nVERTEX\n8\nROCKER\n10\n{x:.3f}\n20\n{y:.3f}\n30\n0.0\n'
    return s + '0\nSEQEND\n'
txt = '0\nSECTION\n2\nENTITIES\n' + dxf_poly(list(sk.exterior.coords)[:-1]) + ''.join(dxf_poly(list(r.coords)[:-1]) for r in sk.interiors) + '0\nENDSEC\n0\nEOF\n'
open('rocker-topopt-right-side.dxf', 'w').write(txt)
# --- printable mock-up (16 mm, rounded edges) and picture
import trimesh
man = rounded_slab(part2d, DS.T_PLATE, DS.EDGE_R)
mesh = man.to_mesh(); tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)
assert tm.is_watertight
tm.export('rocker-topopt-mockup.stl'); print('volume cm3', round(tm.volume/1000, 1), 'extents', tm.extents.round(1))
DS.write_3mf([('Rocker topopt mock-up', tm, (10 - tm.bounds[0][0], 10 - tm.bounds[0][1]))], 'rocker-topopt-mockup.3mf')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(18, 9))
def fillg(ax, gm, **k):
    for gg in (gm.geoms if hasattr(gm, 'geoms') else [gm]):
        q = np.array(gg.exterior.coords); ax.fill(q[:, 0], q[:, 1], **k)
        for r in gg.interiors:
            q = np.array(r.coords); ax.fill(q[:, 0], q[:, 1], color='white')
ax = axs[0]
rhoS = rho.T
ext = [g['minx'], g['minx'] + g['nelx']*H, g['miny'], g['miny'] + g['nely']*H]
img = affinity  # placeholder
fillg(ax, to_sketch(DS.arm_sw), color='#9aa4ad', alpha=.4, lw=0); fillg(ax, to_sketch(DS.shk_sw), color='#3b6ea8', alpha=.2, lw=0)
q = np.array(to_sketch(Polygon(json.load(open('joel-sketch-outline-rocker-coords.json'))['outline'])).exterior.coords); ax.plot(q[:, 0], q[:, 1], 'k--', lw=1.2, label='your sketch')
fillg(ax, sk, color='#e07a2e', alpha=.95, lw=0)
ax.legend(loc='lower left'); ax.set_aspect('equal'); ax.grid(alpha=.3)
ax.set_title('Optimised rocker, right side at full droop (as your sketch)\nGrey: arm sweep. Blue: shock body sweep (guess). Dashed: your sketch')
ax = axs[1]
for p, col, lab in ((poses[0], '#2e7d32', 'droop'), (min(poses, key=lambda q: abs(q['th'] + 13.7*math.pi/180)), '#f9a825', 'sag'), (poses[-1], '#c62828', 'bump')):
    a = unary_union([arm_to_world(x, p['th']) for x in arm_band]); a = affinity.scale(a, -1, 1, origin=(0, 0))
    for gg in (a.geoms if hasattr(a, 'geoms') else [a]):
        q = np.array(gg.exterior.coords); ax.plot(q[:, 0], q[:, 1], color=col, ls='--', lw=1.3)
    rk = affinity.scale(affinity.translate(affinity.rotate(part2d, p['rang'], origin=(0, 0), use_radians=True), *p['R']), -1, 1, origin=(0, 0))
    fillg(ax, rk, color=col, alpha=.3, lw=0); ax.plot([], [], color=col, lw=6, alpha=.4, label=lab)
    ax.plot([-p['D'][0], -p['lug'][0]], [p['D'][1], p['lug'][1]], color=col, lw=4)
ax.plot(0, 0, 'k+', ms=14); ax.legend(); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title('On the bike, right side: droop / sag / bump. Dashed: arm cross-member + lug')
plt.tight_layout(); plt.savefig('rocker-topopt.png', dpi=75)
