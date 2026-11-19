import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse
R = np.array([[1, 0, 0], [0, 0.8824, -0.4705], [0, 0.4705, 0.8824]]); p0 = np.array([2.6, -16.2, -9.4])
L2S = lambda P: p0 + np.asarray(P, float) @ R
Pf = L2S(np.load('Pf.npy')); Pr = L2S(np.load('Pr.npy')); sw = L2S(np.load('sw40.npy'))
rng = np.random.default_rng(1)
pf = Pf[rng.choice(len(Pf), 60000)]; pr = Pr[rng.choice(len(Pr), 60000)]
# sweep envelope (side), within +-95 lateral
S = sw[(np.abs(sw[:, 0]) < 95)]
H, xe, ye = np.histogram2d(-S[:, 1], S[:, 2], bins=[np.arange(-200, 260, 3), np.arange(0, 520, 3)])
XC, YC = (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2
# front envelope
Hf, fxe, fye = np.histogram2d(sw[:, 0], sw[:, 2], bins=[np.arange(-200, 200, 3), np.arange(0, 520, 3)])
# bosses (scan) A/B both sides
BOSS = {'A': (73.8, 112.6), 'B': (43.2, 55.3)}  # (Y, Z)
K = '#1b1b1b'; WH = '#f5f5f2'; RED = '#d0202a'; BLU = '#1d3f9a'; CF = '#2e2e30'; GLASS = '#a9cfe3'
LAMP = '#ffd75e'; TAB = '#1a5fe0'; DASH = '#19b36b'
def chaikin(P, n=3):
    P = np.asarray(P, float)
    for _ in range(n):
        Q = []
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]; Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        P = np.array(Q)
    return P
def ctx_side(ax):
    ax.contourf(XC, YC, (H.T > 0).astype(float), levels=[.5, 1.5], colors=['#fbe9e9'], zorder=0)
    ax.contour(XC, YC, (H.T > 0).astype(float), levels=[.5], colors=['#d04040'], linewidths=1.2, linestyles='--', zorder=2)
    ax.scatter(-pr[:, 1], pr[:, 2], s=.3, c='#c9b0b0', lw=0, zorder=1)
    ax.scatter(-pf[:, 1], pf[:, 2], s=.35, c='#555', lw=0, zorder=1)
    for k, (y, z) in BOSS.items():
        ax.add_patch(Circle((-y, z), 10, fc='#1e8449', ec='k', zorder=9)); ax.text(-y - 26, z - 4, k, color='#1e8449', weight='bold', zorder=9)
    ax.set_aspect('equal'); ax.set_xlim(-120, 230); ax.set_ylim(20, 470); ax.axis('off')
def ctx_front(ax):
    s = pr[:, 1] < 40; ax.scatter(pr[s, 0], pr[s, 2], s=.3, c='#c9b0b0', lw=0, zorder=1)
    s = pf[:, 1] < 60; ax.scatter(pf[s, 0], pf[s, 2], s=.35, c='#555', lw=0, zorder=1)
    ax.set_aspect('equal'); ax.set_xlim(-140, 140); ax.set_ylim(20, 470); ax.axis('off')
REC = []
def P(ax, pts, fc, z=5, ec=K, lw=1.3, smooth=0, alpha=1):
    pts = chaikin(pts, smooth) if smooth else np.asarray(pts, float)
    if getattr(ax, '_side', False) and z >= 4 and fc != '#555': REC.append(pts)
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha))
def wishbone(ax, front=False):
    # mount bracket: neck through fork gap to the head-tube front, splitting to bosses A and B each side
    if not front:
        P(ax, [(-74, 102), (-74, 123), (-30, 160), (40, 175), (52, 150), (-10, 120), (-43, 45), (-43, 66), (-25, 110)], '#555', 3, lw=1)
    else:
        P(ax, [(-41, 50), (-33, 50), (-33, 120), (-28, 160), (28, 160), (33, 120), (33, 50), (41, 50), (41, 125), (34, 170), (-34, 170), (-41, 125)], '#555', 3, lw=1)
def lamps_side(ax, x, z, d=76):
    P(ax, [(x - 60, z - 30), (x - 4, z - d / 2), (x - 4, z + d / 2), (x - 60, z + 30)], '#333', 6)
    ax.add_patch(Ellipse((x, z), 14, d, fc=LAMP, ec=K, zorder=7))
def lamps_front(ax, z, d=76, c=44):
    for s in (-1, 1):
        ax.add_patch(Circle((s * c, z), d / 2 + 4, fc='#222', ec=K, zorder=7)); ax.add_patch(Circle((s * c, z), d / 2 - 3, fc=LAMP, ec=K, zorder=8))
        ax.add_patch(Circle((s * c, z), d / 5, fc='#fff3c0', ec='none', zorder=9))
def tablet_side(ax, a, b):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=TAB, lw=6, solid_capstyle='butt', zorder=8)
def dash_side(ax, a, b):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=DASH, lw=6, solid_capstyle='butt', zorder=8)

CONCEPTS = []
# ---------------------------------------------------------------- 1 modern Dakar slim wedge
def c1(ax, fx):
    ctx_side(ax); wishbone(ax)
    P(ax, [(52, 150), (150, 160), (160, 175), (135, 255), (110, 300), (40, 300), (40, 160)], WH, 5)   # lower body
    P(ax, [(150, 160), (160, 175), (150, 205), (55, 190), (52, 150)], CF, 6)                         # carbon chin
    P(ax, [(152, 214), (143, 238), (60, 228), (58, 210)], RED, 6, ec='none'); P(ax, [(141, 244), (136, 258), (62, 248), (61, 236)], BLU, 6, ec='none')
    lamps_side(ax, 150, 222, 70)
    P(ax, [(110, 300), (40, 300), (22, 365), (60, 378)], WH, 5)                                     # upper body
    P(ax, [(110, 300), (60, 378), (75, 430), (88, 428)], GLASS, 4, alpha=.8)                          # screen
    tablet_side(ax, (20, 368), (64, 382)); dash_side(ax, (40, 300), (24, 362))
    ctx_front(fx); wishbone(fx, True)
    P(fx, [(-88, 160), (88, 160), (95, 255), (70, 300), (-70, 300), (-95, 255)], WH, 5)
    P(fx, [(-88, 160), (88, 160), (80, 190), (-80, 190)], CF, 6)
    P(fx, [(-70, 300), (70, 300), (62, 378), (-62, 378)], WH, 5); P(fx, [(-52, 330), (52, 330), (44, 430), (-44, 430)], GLASS, 4, alpha=.8)
    P(fx, [(-95, 255), (95, 255), (92, 262), (-92, 262)], RED, 6, ec='none')
    lamps_front(fx, 222, 70, 44)
    fx.add_patch(Polygon([(-65, 300), (65, 300), (60, 360), (-60, 360)], fc='none', ec=DASH, lw=2, ls='--', zorder=9))
CONCEPTS.append(('1  Modern Dakar wedge', 'Tall narrow white tower, sharp carbon chin, twin lamps low in the nose,\nshort screen. HRC red/blue flash. ~190 wide at the lamps, ~140 up top.', c1))
# ---------------------------------------------------------------- 2 80s Paris-Dakar fairing (rounded)
def c2(ax, fx):
    ctx_side(ax); wishbone(ax)
    P(ax, [(52, 150), (140, 150), (148, 240), (140, 300), (110, 345), (40, 345), (30, 250), (40, 160)], WH, 5, smooth=2)
    P(ax, [(138, 172), (146, 172), (148, 268), (140, 268)], '#ddd', 6)
    P(ax, [(60, 300), (138, 300), (128, 318), (55, 318)], RED, 6, ec='none'); P(ax, [(55, 322), (124, 322), (116, 334), (50, 334)], BLU, 6, ec='none')
    lamps_side(ax, 148, 220, 76)
    P(ax, [(110, 345), (60, 350), (80, 410), (100, 408)], '#7a8fa0', 4, alpha=.85)
    tablet_side(ax, (28, 352), (66, 368)); dash_side(ax, (40, 258), (32, 340))
    ctx_front(fx); wishbone(fx, True)
    P(fx, [(-100, 150), (100, 150), (105, 260), (90, 320), (60, 350), (-60, 350), (-90, 320), (-105, 260)], WH, 5, smooth=2)
    P(fx, [(-96, 168), (96, 168), (96, 270), (-96, 270)], '#e9e9e9', 6, smooth=1)
    P(fx, [(-90, 290), (90, 290), (80, 310), (-80, 310)], RED, 6, ec='none'); P(fx, [(-78, 314), (78, 314), (68, 328), (-68, 328)], BLU, 6, ec='none')
    lamps_front(fx, 220, 76, 46)
    P(fx, [(-55, 345), (55, 345), (48, 410), (-48, 410)], '#7a8fa0', 4, alpha=.85)
CONCEPTS.append(('2  80s Paris-Dakar fairing', 'Rounded white cowl with a flat "number board" face holding the twin lamps,\ntinted bubble screen, tricolour stripes. Most period. ~210 wide.', c2))
# ---------------------------------------------------------------- 3 light skeleton
def c3(ax, fx):
    ctx_side(ax); wishbone(ax)
    P(ax, [(40, 160), (60, 150), (70, 360), (52, 372)], CF, 5)                                         # carbon spine
    P(ax, [(70, 185), (150, 190), (152, 255), (70, 262)], CF, 5)                                      # lamp cowl
    lamps_side(ax, 152, 222, 70)
    P(ax, [(60, 270), (36, 270), (28, 360), (52, 362)], '#444', 6); dash_side(ax, (36, 272), (28, 356))
    P(ax, [(20, 370), (78, 392), (82, 380), (26, 360)], '#444', 6); tablet_side(ax, (22, 372), (78, 393))
    P(ax, [(120, 262), (140, 262), (100, 340), (90, 338)], GLASS, 4, alpha=.8)
    ctx_front(fx); wishbone(fx, True)
    P(fx, [(-12, 160), (12, 160), (12, 370), (-12, 370)], CF, 5)
    P(fx, [(-92, 185), (92, 185), (92, 260), (-92, 260)], CF, 5, smooth=1)
    lamps_front(fx, 222, 70, 44)
    P(fx, [(-66, 270), (66, 270), (66, 360), (-66, 360)], '#444', 6)
    P(fx, [(-70, 362), (70, 362), (70, 392), (-70, 392)], TAB, 7)
    P(fx, [(-40, 262), (40, 262), (30, 340), (-30, 340)], GLASS, 4, alpha=.6)
CONCEPTS.append(('3  Light skeleton', 'Minimal: carbon spine + small lamp cowl, dash pod and tablet on show.\nLooks light, least carbon to make. ~185 wide at the lamps.', c3))
# ---------------------------------------------------------------- 4 faceted (matches folded tank)
def c4(ax, fx):
    ctx_side(ax); wishbone(ax)
    P(ax, [(52, 150), (155, 168), (100, 215), (45, 200)], '#e9e9e6', 5)
    P(ax, [(155, 168), (150, 250), (100, 215)], WH, 5)
    P(ax, [(45, 200), (100, 215), (150, 250), (118, 305), (38, 300)], '#dcdcd8', 5)
    P(ax, [(38, 300), (118, 305), (60, 372), (22, 362)], '#ececea', 5)
    P(ax, [(118, 305), (88, 420), (78, 418), (60, 372)], GLASS, 4, alpha=.8)
    P(ax, [(150, 250), (154, 262), (60, 248), (58, 236)], RED, 6, ec='none')
    lamps_side(ax, 152, 210, 70)
    tablet_side(ax, (22, 364), (60, 376)); dash_side(ax, (38, 300), (24, 358))
    ctx_front(fx); wishbone(fx, True)
    P(fx, [(-60, 150), (60, 150), (92, 200), (0, 230), (-92, 200)], '#e9e9e6', 5)
    P(fx, [(-92, 200), (0, 230), (92, 200), (96, 255), (60, 305), (-60, 305), (-96, 255)], WH, 5)
    P(fx, [(-60, 305), (60, 305), (70, 340), (40, 372), (-40, 372), (-70, 340)], '#dcdcd8', 5)
    P(fx, [(-40, 330), (40, 330), (30, 420), (-30, 420)], GLASS, 4, alpha=.8)
    P(fx, [(-96, 255), (96, 255), (92, 266), (-92, 266)], RED, 6, ec='none')
    lamps_front(fx, 210, 70, 44)
CONCEPTS.append(('4  Faceted carbon', 'Low-poly folded facets to match your faceted tank, crisp creases,\nsharp beak. Easy flat-panel moulds. ~190 wide.', c4))

CLR = {}
fig = plt.figure(figsize=(20, 22))
for i, (title, desc, fn) in enumerate(CONCEPTS):
    r, c = divmod(i, 2)
    x0, y0 = 0.02 + c * 0.49, 0.52 - r * 0.47
    ax = fig.add_axes([x0, y0, 0.30, 0.40]); fx = fig.add_axes([x0 + 0.29, y0, 0.18, 0.40])
    ax._side = True; REC.clear(); fn(ax, fx)
    from matplotlib.path import Path
    hw = {0: 95, 1: 105, 2: 92, 3: 96}[i]; Ssw = sw[np.abs(sw[:, 0]) < hw]; Q = np.c_[-Ssw[:, 1], Ssw[:, 2]]
    Q = Q[(Q[:, 0] > 0) & (Q[:, 1] > 100)]
    inside = any(Path(p).contains_points(Q).any() for p in REC)
    from scipy.spatial import cKDTree
    E = np.vstack([np.linspace(p[j], p[(j+1) % len(p)], 30) for p in REC for j in range(len(p))])
    dmin = cKDTree(Q).query(E)[0].min()
    print(title, 'overlap' if inside else 'clear', round(dmin, 1))
    CLR[i] = (inside, dmin)
    fig.text(x0, y0 + 0.415, title, fontsize=19, weight='bold'); fig.text(x0, y0 + 0.385, desc, fontsize=11.5, va='top', color='#333')
    ax.text(-115, 30, 'side (front ->)', fontsize=10, color='#666'); fx.text(-135, 30, 'front', fontsize=10, color='#666')
fig.text(0.02, 0.985, 'Nav tower concepts on your bosses (A/B green): all to scale on the frame scan', fontsize=22, weight='bold', va='top')
fig.text(0.02, 0.962, 'Red dashed line = edge of the space the forks, yokes and bars sweep at full 40° lock. Grey bracket = mount (neck through the fork gap, forks to bosses A and B each side).  '
         'Blue = 5" tablet, green = dash pod (130 x 95), yellow = twin ~3" lamps.\nSketches, not final shapes: dimensions are approximate and the lamp/tablet/dash sizes are guesses until you pick the actual parts.', fontsize=12, va='top', color='#333')
fig.savefig('concepts/tower-concepts.png', dpi=70)
