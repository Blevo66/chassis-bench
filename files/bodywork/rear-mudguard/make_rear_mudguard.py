"""Rear mudguard for the XL125R build, retro-modern, printed in 3 glued and pinned sections.

Coordinates match the Fusion frame scan: mm, origin = swingarm pivot, X forward, Y left, Z up.
Run: python3 make_rear_mudguard.py [outdir]
Needs numpy, trimesh, manifold3d (and matplotlib for the preview).
"""
import sys, json, os
import numpy as np
import trimesh
from trimesh import creation

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

# ---------------- inputs (edit these) ----------------
TAB_X, TAB_Z = -340.0, 325.0      # side tabs: X behind pivot, hole height (scan estimate)
TAB_GAP = 146.0                   # outside width of the guard at the tabs = gap between tab inner faces
CROSS_X = -253.0                  # rail cross-member, front P-clip mount
WALL = 3.0                        # shell wall
JOINT_WALL = 8.0                  # thickened wall at the glued joints
PIN_D, PIN_DEPTH = 3.2, 12.0      # 3 mm pins (steel dowel, or 2.85 filament), depth each side
SLOT_HALF = 5.0                   # mount holes are slotted +-5 mm up/down
# tyre and axle at full bump (CRF250 arm 580 mm, 2.9 deg up; 18" 110/100 knobby ~ 340 mm radius, 120 wide)
AXLE_BUMP = np.array([-580 * np.cos(np.radians(2.9)), 580 * np.sin(np.radians(2.9))])
TYRE_R, TYRE_HW, TYRE_CORNER = 340.0, 60.0, 25.0
ARM, DROOP, BUMP = 580.0, -24.2, 2.9

# top-centre line of the guard (X, Z), smoothed with a spline
CTRL = [(-200, 312), (-270, 327.4), (-340, 343), (-420, 367), (-500, 386), (-600, 400),
        (-700, 405), (-765, 414)]


def spline(ctrl, n=400):
    from numpy.polynomial import polynomial as P
    c = np.array(ctrl, float)
    # Catmull-Rom through the points
    pts = [c[0]] + list(c) + [c[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = map(np.array, pts[i - 1:i + 3])
        for t in np.linspace(0, 1, 30, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(c[-1])
    out = np.array(out)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(out, axis=0), axis=1))]
    S = np.linspace(0, s[-1], n)
    return np.c_[np.interp(S, s, out[:, 0]), np.interp(S, s, out[:, 1])], S


PATH, ARC = spline(CTRL)
L = ARC[-1]


def at(s):
    x = np.interp(s, ARC, PATH[:, 0]); z = np.interp(s, ARC, PATH[:, 1])
    ds = 1.0
    x2 = np.interp(min(s + ds, L), ARC, PATH[:, 0]); z2 = np.interp(min(s + ds, L), ARC, PATH[:, 1])
    x1 = np.interp(max(s - ds, 0), ARC, PATH[:, 0]); z1 = np.interp(max(s - ds, 0), ARC, PATH[:, 1])
    t = np.array([x2 - x1, z2 - z1]); t /= np.linalg.norm(t)
    n = np.array([-t[1], t[0]])
    if n[1] < 0: n = -n
    return np.array([x, z]), t, n


def s_of_x(X):
    return float(np.interp(-X, -PATH[:, 0], ARC))


def smooth(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)


def half_width(X):
    return TAB_GAP / 2 + (92 - TAB_GAP / 2) * smooth(-410, -520, -X) if False else \
        TAB_GAP / 2 + (92 - TAB_GAP / 2) * smooth(410, 520, -X)


def skirt(X):
    d = 30 + 12 * smooth(200, 300, -X)            # deepen to 42 at the tabs
    d -= 17 * smooth(380, 480, -X)                # 25 behind the rails
    d -= 7 * smooth(600, 740, -X)                 # 18 at the tail
    return d


CROWN, CHAMF = 6.0, 12.0


def outer_profile(X, n_top=24):
    W = half_width(X); D = skirt(X)
    ys = np.linspace(-(W - CHAMF), W - CHAMF, n_top)
    top = [(y, CROWN * (1 - (y / (W - CHAMF)) ** 2)) for y in ys]
    mid = -(CHAMF + (D - CHAMF) * 0.5)
    return np.array([(-W, -D), (-W, mid), (-W, -CHAMF)] + top + [(W, -CHAMF), (W, mid), (W, -D)])


def offset_inward(prof, t):
    """Offset a 2D open polyline (y,h) towards the inside (downwards/inwards)."""
    p = prof; n = len(p); out = np.zeros_like(p)
    seg = np.diff(p, axis=0); seg /= np.linalg.norm(seg, axis=1)[:, None]
    segn = np.c_[seg[:, 1], -seg[:, 0]]          # right-hand normal: points inside for left->right over the top
    for i in range(n):
        if i == 0: nn = segn[0]; k = 1
        elif i == n - 1: nn = segn[-1]; k = 1
        else:
            nn = segn[i - 1] + segn[i]; nn /= np.linalg.norm(nn); k = 1 / max(np.dot(nn, segn[i]), 0.5)
        out[i] = p[i] + nn * t * k
    return out


def wall_at(s, s0, s1, joints_lo, joints_hi):
    t = WALL
    if joints_lo: t = max(t, WALL + (JOINT_WALL - WALL) * (1 - smooth(10, 16, s - s0)))
    if joints_hi: t = max(t, WALL + (JOINT_WALL - WALL) * (1 - smooth(10, 16, s1 - s)))
    return t


def to3d(s, prof):
    c, t, n = at(s)
    pts = np.zeros((len(prof), 3))
    pts[:, 0] = c[0] + prof[:, 1] * n[0]
    pts[:, 1] = prof[:, 0]
    pts[:, 2] = c[1] + prof[:, 1] * n[1]
    return pts


def loft(s0, s1, jlo, jhi, step=2.0):
    ss = np.unique(np.r_[np.arange(s0, s1, step), s1])
    rings = []
    for s in ss:
        X = at(s)[0][0]
        o = outer_profile(X)
        i = offset_inward(o, wall_at(s, s0, s1, jlo, jhi))
        ring = np.vstack([to3d(s, o), to3d(s, i[::-1])])
        rings.append(ring)
    m = len(rings[0]); V = np.vstack(rings); F = []
    for k in range(len(rings) - 1):
        a, b = k * m, (k + 1) * m
        for j in range(m):
            j2 = (j + 1) % m
            F += [[a + j, b + j, b + j2], [a + j, b + j2, a + j2]]
    h = m // 2
    for base, flip in [(0, True), ((len(rings) - 1) * m, False)]:
        for j in range(h - 1):
            q = [base + j, base + j + 1, base + m - 2 - j, base + m - 1 - j]
            tri = [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            F += [t[::-1] for t in tri] if flip else tri
    mesh = trimesh.Trimesh(V, np.array(F), process=True)
    trimesh.repair.fix_winding(mesh)
    if mesh.volume < 0: mesh.invert()
    return mesh


def cyl_along(p, axis, r, length, sections=32):
    c = creation.cylinder(radius=r, height=length, sections=sections)
    z = np.array([0, 0, 1.0]); a = np.asarray(axis, float); a /= np.linalg.norm(a)
    R = trimesh.geometry.align_vectors(z, a)
    c.apply_transform(R); c.apply_translation(p)
    return c


def world(s, y, h):
    c, t, n = at(s); return np.array([c[0] + h * n[0], y, c[1] + h * n[1]])


def build():
    s_tab, s_cross = s_of_x(TAB_X), s_of_x(CROSS_X)
    cuts = [0, L * 0.34, L * 0.67, L]
    # keep the tab and cross-member mounts away from joints
    parts, adds, subs = [], [], []
    # mount pads + slotted holes through the skirts at the tabs
    c, t, n = at(s_tab)
    h_tab = (TAB_Z - c[1]) / n[1]
    W = half_width(TAB_X)
    for sgn in (1, -1):
        adds.append(cyl_along(world(s_tab, sgn * (W - WALL - 1.5), h_tab), [0, 1, 0], 12, 3.2))
        for dh in np.linspace(-SLOT_HALF, SLOT_HALF, 11):
            subs.append(cyl_along(world(s_tab, sgn * W, h_tab + dh), [0, 1, 0], 3.3, 30))
    # front P-clip hole on top, under the cross-member
    adds.append(cyl_along(world(s_cross, 0, CROWN - WALL - 2), at(s_cross)[2].tolist()[:1] + [0] + at(s_cross)[2].tolist()[1:], 12, 4))
    subs.append(cyl_along(world(s_cross, 0, 0), [at(s_cross)[2][0], 0, at(s_cross)[2][1]], 3.3, 40))
    # plate-hanger holes near the tail
    s_pl = L - 45
    nn = at(s_pl)[2]
    for y in (-30, 30):
        adds.append(cyl_along(world(s_pl, y, CROWN * (1 - (y / (half_width(at(s_pl)[0][0]) - CHAMF)) ** 2) - WALL - 2),
                              [nn[0], 0, nn[1]], 10, 4))
        subs.append(cyl_along(world(s_pl, y, 0), [nn[0], 0, nn[1]], 3.3, 40))
    # pin holes at the joints
    for sj in cuts[1:-1]:
        X = at(sj)[0][0]; Wj = half_width(X); Dj = skirt(X)
        tt = at(sj)[1]; ax = [tt[0], 0, tt[1]]
        mid = JOINT_WALL / 2
        pins = [(0, CROWN - mid), (-45, CROWN * (1 - (45 / (Wj - CHAMF)) ** 2) - mid),
                (45, CROWN * (1 - (45 / (Wj - CHAMF)) ** 2) - mid),
                (-(Wj - mid), -Dj * 0.55), (Wj - mid, -Dj * 0.55)]
        for y, h in pins:
            subs.append(cyl_along(world(sj, y, h), ax, PIN_D / 2, 2 * PIN_DEPTH, 20))
    sub = trimesh.boolean.union(subs, engine='manifold')
    for k in range(3):
        m = loft(cuts[k], cuts[k + 1], k > 0, k < 2)
        mine = [a for a in adds if cuts[k] - 1 < s_near(a.centroid) < cuts[k + 1] + 1]
        if mine:
            m = trimesh.boolean.union([m] + mine, engine='manifold')
        m = trimesh.boolean.difference([m, sub], engine='manifold')
        parts.append(m)
    return parts, cuts, dict(s_tab=s_tab, h_tab=h_tab)


def s_near(p):
    d = np.hypot(PATH[:, 0] - p[0], PATH[:, 1] - p[2]); return ARC[np.argmin(d)]


def tyre_sdf(P, axle):
    rho = np.hypot(P[:, 0] - axle[0], P[:, 2] - axle[1]); y = np.abs(P[:, 1])
    # rounded rectangle in (rho, y): rho <= R, |y| <= HW, corner radius
    qx = rho - (TYRE_R - TYRE_CORNER); qy = y - (TYRE_HW - TYRE_CORNER)
    out = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - TYRE_CORNER
    return out


def clearance(parts):
    res = {}
    V = np.vstack([p.vertices for p in parts])
    for ang in np.linspace(DROOP, BUMP, 28):
        ax = np.array([-ARM * np.cos(np.radians(ang)), ARM * np.sin(np.radians(ang))])
        d = tyre_sdf(V, ax)
        res[round(float(ang), 1)] = (float(d.min()), V[np.argmin(d)].round(0).tolist())
    return res


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    parts, cuts, info = build()
    names = []
    for k, p in enumerate(parts):
        nm = f'rear-mudguard-part{k + 1}.stl'
        p.export(os.path.join(OUT, nm)); names.append(nm)
        # print-ready copy: standing on its front face (flat cut), pin holes vertical, no supports
        q = p.copy(); t = at(cuts[k])[1]
        R = trimesh.geometry.align_vectors([t[0], 0, t[1]], [0, 0, 1])
        q.apply_transform(R); q.apply_translation(-q.bounds[0]); q.apply_translation([128 - q.extents[0] / 2, 128 - q.extents[1] / 2, 0])
        q.export(os.path.join(OUT, f'print-part{k + 1}-stand-on-end.stl'))
        print('  print-ready', q.extents.round(0))
        print(nm, 'watertight', p.is_watertight, 'vol cm3', round(p.volume / 1000, 1),
              'extents', p.bounding_box.extents.round(0))
    trimesh.util.concatenate(parts).export(os.path.join(OUT, 'rear-mudguard-assembled.stl'))
    cl = clearance(parts)
    worst = min(cl.items(), key=lambda kv: kv[1][0])
    print('min tyre clearance', worst)
    json.dump(dict(path=PATH.round(1).tolist(), cuts_x=[round(at(c)[0][0], 1) for c in cuts],
                   clearance_bump=cl[BUMP], worst=worst, **{k: float(v) for k, v in info.items()}),
              open(os.path.join(OUT, 'rear-mudguard-info.json'), 'w'), indent=1)
