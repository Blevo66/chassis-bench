import numpy as np, trimesh, json
from scipy.spatial import cKDTree
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
Pf = np.load('Pf.npy'); Pr = np.load('Pr.npy'); sw = np.load('sw40.npy')
R = np.array([[1, 0, 0], [0, 0.8824, -0.4705], [0, 0.4705, 0.8824]]); p0 = np.array([2.6, -16.2, -9.4])
L2S = lambda P: p0 + np.asarray(P, float) @ R
OD, LEN, ID = 20.0, 12.0, 6.8   # M8 boss (6.8 = tap drill, for looks)
# boss centres in local (u back, t up the steering axis), mirrored both sides
SPOTS = {'A_front_upper': (22, 150), 'B_front_lower': (22, 85)}
def surf_v(u, t, side):
    m = (np.abs(Pf[:, 1] - u) < 4) & (np.abs(Pf[:, 2] - t) < 4) & (np.sign(Pf[:, 0]) == side)
    return np.abs(Pf[m, 0]).max()
bosses = []; report = {}
swT = cKDTree(sw); pfT = cKDTree(Pf)
for name, (u, t) in SPOTS.items():
    for side, sname in [(1, 'plusX'), (-1, 'minusX')]:
        v0 = surf_v(u, t, side)
        cyl = trimesh.creation.annulus(r_min=ID / 2, r_max=OD / 2, height=LEN, sections=48)
        # annulus axis is z: rotate so axis is local v, then place base on surface
        T = np.eye(4); T[:3, :3] = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])  # z->v(x), x->u(y), y->t(z)
        cyl.apply_transform(T); cyl.apply_translation([side * (v0 + LEN / 2 - 0.5), u, t])
        pts = cyl.sample(3000)
        dsw = swT.query(pts)[0].min()
        tip = np.array([side * (v0 + LEN), u, t]); rtip = np.hypot(v0 + LEN, u)
        report[f'{name}_{sname}'] = dict(local_u=u, local_t=t, surface_v=round(float(side * v0), 1),
                                         face_v=round(float(side * (v0 + LEN)), 1), clear_to_fork_sweep_mm=round(float(dsw), 1),
                                         scan_xyz_centre_of_face=L2S(tip).round(1).tolist(),
                                         clamp_xyz_centre_of_face=[round(float(-tip[0]), 1), round(float(t - 66.5), 1), round(float(u), 1)])
        bosses.append(cyl)
B = trimesh.util.concatenate(bosses)
Bs = B.copy(); Bs.vertices = L2S(B.vertices); Bs.export('bosses/m8-bosses-scan-coords.stl')
Bc = B.copy(); V = B.vertices; Bc.vertices = np.c_[-V[:, 0], V[:, 2] - 66.5, V[:, 1]]; Bc.export('bosses/m8-bosses-clamp-coords.stl')
json.dump(report, open('bosses/boss-positions.json', 'w'), indent=1)
for k, r in report.items(): print(k, r)
# ---------- figure: side view (local u/t, looking from +X side) and front view
fig, (a, b) = plt.subplots(1, 2, figsize=(16, 8.5), gridspec_kw=dict(width_ratios=[1.25, 1]))
s = Pf[:, 0] > 0; a.scatter(-Pf[s, 1], Pf[s, 2], s=.3, c='#aaa', lw=0)
s = (Pr[:, 0] > 0) & (np.abs(Pr[:, 0]) < 140); a.scatter(-Pr[s, 1], Pr[s, 2], s=.3, c='#e8c4c4', lw=0)
cl = np.array([[-10.9, 66.5], [-10.9, 186.5], [-25.9, 186.5], [-58.5, 156], [-58.5, 66.5], [-10.9, 66.5]])
a.plot(-cl[:, 0], cl[:, 1], color='#c0392b', lw=2, label="your headstock clamp")
for name, (u, t) in SPOTS.items():
    a.add_patch(Circle((-u, t), OD / 2, fc='#1e8449', ec='k', lw=1.5, alpha=.9)); a.add_patch(Circle((-u, t), 4, fc='w', ec='k'))
    a.text(-u - 14, t + 12, name[0], fontsize=16, weight='bold', color='#1e8449')
a.add_patch(Circle((-80, 115), 6, fc='k')); a.text(-130, 100, 'tank boss', fontsize=9)
a.plot([-22, -22], [150, 85], 'g:', lw=1); a.axvline(-8, color='m', ls='--', lw=1); a.text(-6, 200, 'approx weld line\n(guess, ~8 mm\nbehind axis)', color='m', fontsize=9)
a.set_aspect('equal'); a.set_xlim(-200, 80); a.set_ylim(20, 230); a.grid(alpha=.3)
a.set_xlabel('mm  (front of bike to the RIGHT; 0 = steering axis)'); a.set_ylabel('mm up the steering axis')
a.set_title('Side view along the head tube (frame grey, forks/yokes pink)'); a.legend(loc='upper left')
# front-ish view: lateral vs t, at all u
s = Pf[:, 1] > -5; b.scatter(Pf[s, 0], Pf[s, 2], s=.3, c='#aaa', lw=0)
ss = np.random.default_rng(0).choice(len(sw), 150000); b.scatter(sw[ss, 0], sw[ss, 2], s=.2, c='#f2d0d0', lw=0, zorder=0)
for name, (u, t) in SPOTS.items():
    for side in [1, -1]:
        v0 = surf_v(u, t, side)
        b.add_patch(Rectangle((side * v0 if side > 0 else -v0 - LEN, t - OD / 2), LEN, OD, fc='#1e8449', ec='k'))
b.set_aspect('equal'); b.set_xlim(-130, 130); b.set_ylim(20, 230); b.grid(alpha=.3)
b.set_title('Looking from the front (pink haze = everything the forks/yokes\nsweep through at ±40° lock)'); b.set_xlabel('sideways mm')
txt = '  '.join(f"{k[0]}: {min(report[k+'_plusX']['clear_to_fork_sweep_mm'], report[k+'_minusX']['clear_to_fork_sweep_mm'])} mm" for k in SPOTS)
fig.suptitle(f'M8 weld-on bosses, 20 OD x 12 long, 2 a side (A front-upper, B front-lower). Positions approx ±3-5 mm.\nMin clearance from each boss to the fork/yoke sweep at full lock: {txt}', fontsize=11)
plt.tight_layout(); plt.savefig('bosses/m8-bosses-on-scan.png', dpi=85)
