"""Build the rear-suspension scene in the Fusion scan frame (mm, origin = swingarm pivot, X fwd, Y left, Z up).
Writes r/scene.json for page.html. python3 build.py [wheel_travel_from_droop_mm ...]"""
import json, math, sys, numpy as np, trimesh, manifold3d as m3
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
W = '/tmp/claude-0/w/'
D2R = math.pi/180
def rot2(p, a): c, s = math.cos(a), math.sin(a); return np.array([p[0]*c - p[1]*s, p[0]*s + p[1]*c])
def circ(c0, r0, c1, r1):
    d = np.linalg.norm(c1 - c0); a = (r0*r0 - r1*r1 + d*d)/(2*d); h = math.sqrt(max(0, r0*r0 - a*a))
    e = (c1 - c0)/d; m = c0 + a*e; n = np.array([-e[1], e[0]]); return m + h*n, m - h*n
# ---------- arm (Joel's CRF250R STEP) ----------
PIV_M = np.array([188.5, 83.65, -54.0])   # model pivot bore centre
def arm_local(v): return np.c_[v[:, 0] - PIV_M[0], -(v[:, 1] - PIV_M[1]), -(v[:, 2] - PIV_M[2])]   # model is upside down: turn 180 about X
LUG_MODEL = arm_local(np.array([[-20.4, 0, 1.9]]))[0][[0, 2]]  # lug hole in (X, Z), arm level: (-208.9, -55.9)
BENCH = True   # Joel 31 Oct: render from the Chassis Bench numbers -> lug at the bench's 200 along / 50 below, arm model shifted to suit
LUG = np.array([-200.0, -50.0]) if BENCH else LUG_MODEL
ARM_SHIFT = LUG - LUG_MODEL
# ---------- linkage (Joel's v2 rocker hole centres, 82 dogbone, XR 380/95) ----------
R = np.array([-22.0, -29.0]); T = np.array([55.0, 292.0])
PIV_SK, DOG_SK, SHK_SK = np.array([0, 0.]), np.array([-57.3, -93.9]), np.array([-151.7, 17.6])
rD, DOGL = np.linalg.norm(DOG_SK), 82.0
aD0 = math.atan2(DOG_SK[1], DOG_SK[0])
def pose(beta, prevD=None):
    lug = rot2(LUG, beta)
    c = circ(R, rD, lug, DOGL)
    D = min(c, key=lambda q: np.linalg.norm(q - (prevD if prevD is not None else R + DOG_SK)))
    th = math.atan2(D[1] - R[1], D[0] - R[0]) - aD0
    S = R + rot2(SHK_SK, th)
    return dict(beta=beta, lug=lug, D=D, S=S, th=th, L=float(np.linalg.norm(S - T)), axle=rot2((-580, 0), beta))
P = []; b = 40*D2R; prev = None
while b > -15*D2R:
    p = pose(b, prev); prev = p['D']; P.append(p); b -= 0.05*D2R
droop = min(P, key=lambda p: abs(p['L'] - 380)); bump = min(P, key=lambda p: abs(p['L'] - 285))
i0, i1 = P.index(droop), P.index(bump); P = P[i0:i1 + 1]
for p in P: p['wt'] = p['axle'][1] - droop['axle'][1]
print('lug (arm level)', LUG.round(1), 'droop arm deg', round(droop['beta']/D2R, 1), 'bump', round(bump['beta']/D2R, 1),
      'vertical travel', round(bump['wt'], 1))
r0 = droop['wt']; rr = []
for k in range(0, len(P) - 20, 20):
    rr.append((P[k+20]['wt'] - P[k]['wt'])/(P[k]['L'] - P[k+20]['L']))
print('ratio', round(rr[0], 2), '->', round(rr[-1], 2), 'rising', round((rr[0]/rr[-1] - 1)*100), '%')
def at_travel(w): return min(P, key=lambda p: abs(p['wt'] - w))
# ---------- meshes ----------
def man(tm): return m3.Manifold(m3.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
def tri(mf): mm = mf.to_mesh(); return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))
def poly_extrude(poly, h):
    t = trimesh.creation.extrude_polygon(poly, h); t.apply_translation((0, 0, -h/2)); return t
def cylY(c, r, L, y0=None, n=48):
    t = trimesh.creation.cylinder(r, L, sections=n); t.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (1, 0, 0)))
    t.apply_translation((c[0], (y0 if y0 is not None else 0), c[1])); return t
pr = json.load(open(W + 'v2_profile.json'))
outer = Polygon(pr['outer']).buffer(-1.2).buffer(2.4, 32).buffer(-1.2, 32).simplify(0.15)
holes = [Polygon(h).buffer(1.2).buffer(-2.4, 32).buffer(1.2, 32).simplify(0.15) for h in pr['holes']]
prof = outer
for h in holes: prof = prof.difference(h)
for c, r in ((PIV_SK, 15), (DOG_SK, 13), (SHK_SK, 13)): prof = prof.union(Point(c).buffer(r, 48))  # bosses, as on Joel's drawing
for c, r in ((PIV_SK, 6.04), (DOG_SK, 5.1), (SHK_SK, 5.1)): prof = prof.difference(Point(c).buffer(r, 48))
TH = 30.0
rk = man(poly_extrude(prof, TH))
slot = trimesh.creation.box((60, 60, 11)); slot.apply_translation((DOG_SK[0] - 18, DOG_SK[1] - 18, 0))   # 11 mm dogbone slot
rk = rk - man(slot)
# soften edges a little via smoothing is overkill; keep crisp machined look
rocker_sk = tri(rk)   # sketch frame: x fwd, y up, z across
def place_rocker(p):
    v = rocker_sk.vertices.copy(); xz = np.array([rot2(q, p['th']) for q in v[:, :2]]) + R
    return trimesh.Trimesh(np.c_[xz[:, 0], 10 + v[:, 2], xz[:, 1]], rocker_sk.faces)
# dogbone: Joel's tapered block, 10 wide at the rocker (on the 10-left line), 38 wide at the lug (centred ~3 right), 82 c-c, 26 deep
def dogbone(p):
    D, Lg = p['D'], p['lug']; u = (Lg - D)/np.linalg.norm(Lg - D)
    a = cylY((0, 0), 13, 10); a.apply_translation((0, 10, 0))
    b = cylY((0, 0), 17, 38); b.apply_translation((82, -3, 0))
    hull = trimesh.convex.convex_hull(np.r_[a.vertices, b.vertices])
    mf = man(hull) - man(cylY((0, 0), 7, 40, 10)) - man(cylY((82, 0), 11, 60, -3))
    t = tri(mf); ang = math.atan2(u[1], u[0])
    xz = np.array([rot2(q, ang) for q in t.vertices[:, [0, 2]]]) + D
    return trimesh.Trimesh(np.c_[xz[:, 0], t.vertices[:, 1], xz[:, 1]], t.faces)
def bolt(c, y, L, r=5):
    shank = cylY(c, r, L, y, 24)
    h1 = trimesh.creation.cylinder(r*1.7, r*0.8, sections=6); h1.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, (1, 0, 0)))
    h1.apply_translation((c[0], y + L/2 - r*0.4, c[1]))
    n1 = h1.copy(); n1.apply_translation((0, -L + r*0.8, 0))
    return trimesh.util.concatenate([shank, h1, n1])
def arm_parts(beta):
    out = {}
    for name, ids in (('arm', [82]), ('armbits', [74, 75, 76, 77, 80, 81]), ('slider', [83]), ('pivotbits', [78, 79])):
        ms = []
        for i in ids:
            t = trimesh.load(f'{W}parts/{i:03d}.stl'); v = arm_local(t.vertices); v[:, 0] += ARM_SHIFT[0]; v[:, 2] += ARM_SHIFT[1]
            xz = np.c_[v[:, 0]*math.cos(beta) - v[:, 2]*math.sin(beta), v[:, 0]*math.sin(beta) + v[:, 2]*math.cos(beta)]
            ms.append(trimesh.Trimesh(np.c_[xz[:, 0], v[:, 1], xz[:, 1]], t.faces))
        m = trimesh.util.concatenate(ms); out[name] = m
    return out
# frame scan, rear loop straightened (it leans ~40 mm left going back)
scan = trimesh.load('/mnt/project-files/frame-scan/fusion/xl125r-frame-scan-full.stl')
v = scan.vertices.copy(); x = v[:, 0]
v[:, 1] -= 0.13*np.clip(-60 - x, 0, None)*np.clip((v[:, 2] - 60)/120, 0, 1)
if False:   # (removed 31 Oct, Joel: frame went bendy) move the scan's head tube onto the bench's (bottom 516 fwd / 365 up vs the scan's ~499 / 435), blended in from x 150 to 430
    wgt = np.clip((x - 150)/280, 0, 1); wgt = wgt*wgt*(3 - 2*wgt)
    v[:, 0] += 17*wgt; v[:, 2] += -70*wgt
scan.vertices = v
def pack(m, digits=1):
    m = m.copy(); m.merge_vertices(); m = trimesh.graph.smooth_shade(m, angle=np.radians(35))
    return dict(v=np.round(m.vertices, digits).ravel().tolist(), i=m.faces.ravel().astype(int).tolist())
scene = dict(scan=pack(scan), arm={k: pack(m) for k, m in arm_parts(0.0).items()}, poses={})
keys = [('sag', at_travel(79)), ('droop', droop), ('bump', bump)]
NF = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for k in range(NF):   # animation frames, droop -> bump -> droop (cosine eased)
    w = bump['wt']*(1 - math.cos(2*math.pi*k/NF))/2
    keys.append((f'f{k:02d}', at_travel(w)))
for key, p in keys:
    objs = {'rocker': pack(place_rocker(p)), 'dogbone': pack(dogbone(p))}
    bolts = [bolt(R, 10, 62, 5), bolt(p['D'], 10, 26, 5), bolt(p['lug'], 3, 66, 6), bolt(T, 10, 60, 5), bolt(p['S'], 10, 66, 5)]
    objs['bolts'] = pack(trimesh.util.concatenate(bolts))
    scene['poses'][key] = dict(objs=objs, S=p['S'].tolist(), T=T.tolist(), L=p['L'], beta=p['beta']/D2R, axle=p['axle'].tolist(), wt=p['wt'])
    print(key, 'arm deg', round(p['beta']/D2R, 1), 'shock', round(p['L'], 1), 'wheel up', round(p['wt'], 1))
json.dump(scene, open(W + 'r/scene.json', 'w'))
