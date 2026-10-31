"""Printable mock-up rocker (and dogbone + pivot spacers) for rocker B with the 82 mm dogbone,
XR250R shock (380 / 95) on the rocker-on-frame layout, Joel's 2007 CRF250 arm.

Side profile is cut automatically: start from the hull of the three bosses, then remove everything the
arm's cross-member and lug (sliced from Joel's arm model across the rocker's width) and the bottom of the
shock sweep through, relative to the rocker, from full droop to full bump, plus a clearance.

Run:  python3 design.py      (needs numpy, shapely, manifold3d, matplotlib)
"""
import math, json
import numpy as np
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import manifold3d as m3
from geom import G, sweep, rot, dist, ARM, ARM_SHIFT, D2R

# ---------------- settings (placeholders marked) ----------------
T_PLATE   = 16.0   # rocker plate thickness = tongue into the XR shock clevis. PLACEHOLDER: set to clevis gap minus ~0.5
T_DOG     = 12.0   # dogbone bar thickness (bolts beside the rocker's right face, lines up with the arm lug centre)
HOLE      = 10.4   # all bolt holes, M10 clearance. Shock bolt is M10 (Joel). Pivot and dogbone bolts PLACEHOLDER: drill out to suit
R_PIV, R_DOG, R_SHK = 17.0, 13.0, 12.5   # boss radii (shock end kept inside the clevis ears' 12-15 mm radius)
CLEAR     = 4.0    # target gap to the arm all through the travel
CLEAR_SHK = 2.0    # target gap to the (placeholder) shock body
FILLET    = 3.0    # corner rounding on the cut
CLEVIS_BRIDGE = 20.0  # PLACEHOLDER: shock bolt centre to the underside of the clevis bridge, along the shock
CLEVIS_HALF   = 20.0  # PLACEHOLDER: half width of the shock body above the bridge (side view)
SPACER_W  = 12.0   # each pivot spacer: (40 mm frame mount - 16 plate) / 2
DOG_LEN   = G['dog']
LUG_HOLE  = 12.4   # arm lug bolt: Joel's arm model has a 12.8 mm hole, so likely M12. Check before printing

R0 = np.array(G['R']); Dl = np.array([G['rD'], 0.0])
Sl = np.array([G['rS']*math.cos(G['incl']*D2R), G['rS']*math.sin(G['incl']*D2R)])

arm_band = [Polygon(p) for p in json.load(open('arm_section_rocker_band.json'))]
arm_red  = Polygon([(q[0]+ARM_SHIFT[0], q[1]+ARM_SHIFT[1]) for q in ARM['cross']])  # the bench's own outline, for the report

def arm_to_world(poly, th):  # arm coords (along, above the pivot-axle line) -> frame coords
    return affinity.rotate(poly, th, origin=(0, 0), use_radians=True)
def world_to_rocker(geom, p):  # frame coords -> rocker coords (R at origin, D on +x)
    g = affinity.translate(geom, -p['R'][0], -p['R'][1])
    return affinity.rotate(g, -p['rang'], origin=(0, 0), use_radians=True)
def shock_end(p):  # placeholder for the bottom of the shock above the clevis, in frame coords
    S = np.array(p['S']); top = np.array(G['shockTop']); u = (top - S)/np.linalg.norm(top - S); n = np.array([-u[1], u[0]])
    a, b = S + u*CLEVIS_BRIDGE, S + u*120
    return Polygon([a + n*CLEVIS_HALF, b + n*CLEVIS_HALF, b - n*CLEVIS_HALF, a - n*CLEVIS_HALF])

poses = sweep()
poses = poses[::5] + [poses[-1]]   # every 0.25 deg
arm_sw = unary_union([world_to_rocker(arm_to_world(a, p['th']), p) for p in poses for a in arm_band])
shk_sw = unary_union([world_to_rocker(shock_end(p), p) for p in poses])

bosses = unary_union([Point(0, 0).buffer(R_PIV, 64), Point(*Dl).buffer(R_DOG, 64), Point(*Sl).buffer(R_SHK, 64)])
hull = bosses.convex_hull
body = hull.difference(arm_sw.buffer(CLEAR, 64)).difference(shk_sw.buffer(CLEAR_SHK, 64))
body = unary_union([body, bosses])
if isinstance(body, MultiPolygon):
    body = max(body.geoms, key=lambda g: g.intersects(Point(0, 0)) * 1e9 + g.area)
# round off the sharp corners left by the cut, keeping the bosses whole
body = unary_union([body.buffer(-FILLET, 64).buffer(FILLET, 64), bosses])
assert body.geom_type == 'Polygon', body.geom_type

def gap_report():
    out = []
    for p in poses:
        rk = affinity.rotate(body, p['rang'], origin=(0, 0), use_radians=True); rk = affinity.translate(rk, *p['R'])
        a = unary_union([arm_to_world(x, p['th']) for x in arm_band]); r = arm_to_world(arm_red, p['th'])
        out.append((p['th']/D2R, rk.distance(a), rk.distance(r), rk.distance(shock_end(p))))
    return out
rep = gap_report()
mi = min(rep, key=lambda r: r[1]); mr = min(rep, key=lambda r: r[2]); ms = min(rep, key=lambda r: r[3])
print(f"min gap to arm (model slice): {mi[1]:.1f} mm at arm {mi[0]:.1f} deg")
print(f"min gap to bench cross-member outline: {mr[2]:.1f} mm at arm {mr[0]:.1f} deg")
print(f"min gap to shock body placeholder: {ms[3]:.1f} mm at arm {ms[0]:.1f} deg")
print(f'corridor between arm and shock sweeps: {arm_sw.distance(shk_sw):.1f} mm')
print('rocker area', round(body.area), 'bbox', [round(v) for v in body.bounds])

# ---------------- 3D ----------------
def cs(poly):
    return m3.CrossSection([list(poly.exterior.coords)[:-1]] + [list(i.coords)[:-1] for i in poly.interiors], m3.FillRule.EvenOdd)
def holes(pts):
    return unary_union([Point(*q).buffer(HOLE/2, 64) for q in pts])
# lay the rocker out with the pivot-to-shock line roughly along X for the bed
rocker2d = body.difference(holes([(0, 0), tuple(Dl), tuple(Sl)]))
rocker = m3.Manifold.extrude(cs(rocker2d), T_PLATE)

dog2d = unary_union([Point(0, 0).buffer(R_DOG, 64), Point(DOG_LEN, 0).buffer(R_DOG, 64), Polygon([(0, -9), (DOG_LEN, -9), (DOG_LEN, 9), (0, 9)])])
dog2d = dog2d.difference(holes([(0, 0)])).difference(Point(DOG_LEN, 0).buffer(LUG_HOLE/2, 64))
dog = m3.Manifold.extrude(cs(dog2d), T_DOG)

sp2d = Point(0, 0).buffer(15, 64).difference(Point(0, 0).buffer(HOLE/2, 64))
spacer = m3.Manifold.extrude(cs(sp2d), SPACER_W)
lug_sp = m3.Manifold.extrude(cs(Point(0, 0).buffer(12, 64).difference(Point(0, 0).buffer(LUG_HOLE/2, 64))), (41 - T_DOG)/2)

def save(man, name):
    mesh = man.to_mesh(); v = np.asarray(mesh.vert_properties)[:, :3]; f = np.asarray(mesh.tri_verts)
    import trimesh; tm = trimesh.Trimesh(v, f, process=True)
    assert tm.is_watertight, name
    tm.export(name + '.stl')
    return tm
parts = {}
parts['rocker-B82-mockup'] = save(rocker, 'rocker-B82-mockup')
parts['dogbone-82-mockup'] = save(dog, 'dogbone-82-mockup')
parts['pivot-spacer-12mm'] = save(spacer, 'pivot-spacer-12mm')
parts['lug-packer-14.5mm'] = save(lug_sp, 'lug-packer-14.5mm')
import trimesh
json.dump({'rocker_outline_rocker_coords': [list(map(lambda v: round(v, 2), c)) for c in body.exterior.coords],
           'R': [0, 0], 'D': Dl.round(2).tolist(), 'S': Sl.round(2).tolist(),
           'note': 'rocker coords: pivot at 0,0, dogbone eye on +x; S is the shock bolt. Looking at the bike from the LEFT, +x is the pivot-to-dogbone-eye direction.'},
          open('rocker-B82-outline.json', 'w'), indent=1)

# ---------------- picture ----------------
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(21, 8))
names = [('Full droop (shock 380)', poses[0]), ('Mid travel', poses[len(poses)//2]), ('Full bump (shock 285)', poses[-1])]
for ax, (t, p) in zip(axs, names):
    for a in arm_band:
        q = np.array(arm_to_world(a, p['th']).exterior.coords); ax.fill(q[:, 0], q[:, 1], color='#9aa4ad', alpha=.8)
    so = np.array(arm_to_world(Polygon([(q[0]+ARM_SHIFT[0], q[1]+ARM_SHIFT[1]) for q in ARM['side']]), p['th']).exterior.coords)
    ax.plot(so[:, 0], so[:, 1], color='#55606a', lw=1, ls='--')
    rk = affinity.translate(affinity.rotate(body, p['rang'], origin=(0, 0), use_radians=True), *p['R'])
    q = np.array(rk.exterior.coords); ax.fill(q[:, 0], q[:, 1], color='#e07a2e', alpha=.9)
    sh = np.array(shock_end(p).exterior.coords); ax.fill(sh[:, 0], sh[:, 1], color='#3b6ea8', alpha=.35)
    ax.plot([p['S'][0], G['shockTop'][0]], [p['S'][1], G['shockTop'][1]], color='#3b6ea8', lw=2)
    ax.plot([p['D'][0], p['lug'][0]], [p['D'][1], p['lug'][1]], color='#2a2a2a', lw=7, solid_capstyle='round')
    for c in (p['R'], p['D'], p['S'], p['lug']): ax.add_patch(plt.Circle(c, HOLE/2, color='white', zorder=5))
    ax.plot(0, 0, 'k+', ms=14)
    ax.set_xlim(-40, 260); ax.set_ylim(-160, 130); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_title(f"{t}: arm {p['th']/D2R:.1f}°, shock {p['L']:.0f} mm")
axs[0].text(-35, 120, 'Left side view, front of bike to the left.\nGrey: arm cross-member + lug cut across the rocker\'s width.\nDashed: arm legs (outboard of the rocker).\nOrange: mock-up rocker. Blue: shock (clevis body is a placeholder).', va='top', fontsize=9)
plt.tight_layout(); plt.savefig('rocker-B82-mockup-preview.png', dpi=80)

fig, ax = plt.subplots(figsize=(8, 9))
q = np.array(body.exterior.coords); ax.fill(q[:, 0], q[:, 1], color='#e07a2e')
for c, n in ((( 0, 0), 'pivot (frame)'), (tuple(Dl), 'dogbone'), (tuple(Sl), 'shock M10')):
    ax.add_patch(plt.Circle(c, HOLE/2, color='white')); ax.annotate(n, c, xytext=(c[0]+14, c[1]+4), fontsize=11)
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(f'Rocker B mock-up, {T_PLATE:.0f} mm plate. Eyes 111 / 152.7 mm, 65° apart')
plt.savefig('rocker-B82-mockup-profile.png', dpi=80, bbox_inches='tight')

# ---------------- 3MF for Bambu Studio: each part its own object, laid out on one plate ----------------
import zipfile
def write_3mf(objs, dst):
    res, items = [], []
    for i, (name, tm, off) in enumerate(objs, 1):
        v = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in tm.vertices)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tm.faces)
        res.append(f'<object id="{i}" type="model" name="{name}"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {off[0]:.2f} {off[1]:.2f} 0"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + "".join(res) +
             '</resources><build>' + "".join(items) + '</build></model>')
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)
bx = body.bounds; ox, oy = 10 - bx[0], 10 - bx[1]
dog_up = parts['dogbone-82-mockup'].copy(); dog_up.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [0, 0, 1]))
objs = [('Rocker B mock-up', parts['rocker-B82-mockup'], (ox, oy)),
        ('Dogbone 82 mock-up', dog_up, (183, 30)),
        ('Pivot spacer 12 mm', parts['pivot-spacer-12mm'], (225, 32)),
        ('Pivot spacer 12 mm', parts['pivot-spacer-12mm'], (225, 68)),
        ('Lug packer 14.5 mm', parts['lug-packer-14.5mm'], (225, 100)),
        ('Lug packer 14.5 mm', parts['lug-packer-14.5mm'], (225, 128))]
write_3mf(objs, 'rocker-B82-mockup-plate.3mf')
mx = max(o[2][0] + o[1].bounds[1][0] for o in objs); my = max(o[2][1] + o[1].bounds[1][1] for o in objs)
print('3mf plate extent', round(mx), round(my), '(Bambu bed 256)')
