import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
Pf = np.load('Pf.npy'); Pr = np.load('Pr.npy'); sw = np.load('sw40.npy')
R = np.array([[1, 0, 0], [0, 0.8824, -0.4705], [0, 0.4705, 0.8824]]); p0 = np.array([2.6, -16.2, -9.4])
L2S = lambda P: p0 + np.asarray(P, float) @ R
def side(P):  # local (v,u,t) -> plot (fwd, up) in scan
    S = L2S(P); return np.c_[-S[..., 1], S[..., 2]]
STEEL = '#1f5fa8'; TUBE = '#111'; CL = '#c0392b'; TOW = '#e67e22'
fig = plt.figure(figsize=(17, 9.5))
ax = fig.add_axes([0.03, 0.08, 0.55, 0.82]); bx = fig.add_axes([0.62, 0.08, 0.36, 0.82])
# ---------- side view
f = side(Pf); ax.scatter(f[::3, 0], f[::3, 1], s=0.3, c='#999', lw=0)
r = side(Pr); ax.scatter(r[::3, 0], r[::3, 1], s=0.3, c='#d9b3b3', lw=0)
# window plate (outside head box), behind the tank boss
plate = np.array([[100, 70], [100, 158], [150, 165], [205, 140], [200, 88], [165, 66], [130, 60]], float)
pl = np.c_[np.full(len(plate), 32), plate]; ax.add_patch(Polygon(side(pl), fc=STEEL, alpha=.35, ec=STEEL, lw=2))
# folded edge line
ax.plot(*side(np.c_[np.full(4, 32), plate[[1, 2, 3, 4]]]).T, color=STEEL, lw=4, alpha=.6)
# corner block filling window front corner
blk = np.array([[121, 102], [128, 84], [148, 80], [152, 118], [140, 126]], float)
ax.add_patch(Polygon(side(np.c_[np.zeros(5), blk]), fc='#555', ec='k', lw=1.5, hatch='///', alpha=.8))
for b in [[140, 102], [175, 92]]:
    ax.add_patch(Circle(side([0, *b])[0], 5, fc='w', ec='k', lw=1.5))
# headstock clamp (Joel's) - local u = clamp Z, t = clamp Y + 66.5
cl = np.array([[-10.9, 66.5], [-10.9, 186.5], [-25.9, 186.5], [-37, 160], [-58.5, 156], [-58.5, 66.5]], float)
ax.add_patch(Polygon(side(np.c_[np.zeros(len(cl)), cl[:, 0], cl[:, 1]]), fc=CL, alpha=.5, ec=CL, lw=1.5))
# hoops (side view: straight runs at t 76.5 and 149.6 from plate to clamp keel holes)
for t in [76.5, 149.6]:
    hp = np.array([[33, 110, t], [42, 40, t], [45, 0, t], [35, -30, t], [12, -48.5, t]])
    ax.plot(*side(hp).T, color=TUBE, lw=6, solid_capstyle='round')
    ax.add_patch(Circle(side([0, -48.5, t])[0], 4, fc='w', ec='k'))
# tower (schematic, in plot coords; rear edge kept ahead of the 40 deg fork sweep)
k1=side([0,-48.5,76.5])[0];k2=side([0,-48.5,149.6])[0]
tow=np.array([[50,120],[150,140],[160,230],[120,335],[15,335],[20,230]],float)
ax.add_patch(Polygon(tow, fc='none', ec=TOW, lw=2.5, ls='--'))
ax.text(70,250,'tower\n(shape still\nyour pick)', color=TOW, fontsize=10, ha='left')
for k,g in [(k1,[55,135]),(k2,[40,200])]:
    ax.plot([k[0],g[0]],[k[1],g[1]],color=TUBE,lw=5); ax.add_patch(Circle(g, 6, fc=TOW, ec='k'))
ax.annotate('rubber grommets', [40,200], [-60,380], color=TOW, arrowprops=dict(arrowstyle='->', color=TOW))
ax.annotate('window plates, 3 mm steel,\nfolded edge, frame colour\n(one each side)', side([32, 170, 140])[0], side([32, 170, 140])[0] + [-60, 90], color=STEEL, arrowprops=dict(arrowstyle='->', color=STEEL), fontsize=10)
ax.annotate('block keyed into the\nwindow front corner\n+ 2 through-bolts\n(stops any twist)', side([0, 135, 95])[0], side([0, 135, 95])[0] + [-20, -150], arrowprops=dict(arrowstyle='->'), fontsize=10)
ax.annotate('2 bent steel tube hoops\n(16-19 mm, black), round the\nhead tube, bolt to your clamp\'s\nkeel holes at the front', side([40, 40, 149.6])[0], side([40, 40, 149.6])[0] + [-210, 140], arrowprops=dict(arrowstyle='->'), fontsize=10)
ax.annotate('your headstock clamp\n(hidden, painted black)', side([0, -40, 120])[0], side([0, -40, 120])[0] + [-60, -170], color=CL, arrowprops=dict(arrowstyle='->', color=CL), fontsize=10)
ax.annotate('tank boss stays free\n(plates start behind it)', side([40, 85, 115])[0], side([40, 85, 115])[0] + [20, -120], arrowprops=dict(arrowstyle='->'), fontsize=9, color='#444')
ax.set_aspect('equal'); ax.set_xlim(-330, 220); ax.set_ylim(-80, 420); ax.grid(alpha=.25)
ax.set_title('SIDE VIEW from the right (front is to the RIGHT), scan mm. Grey = frame, pink = forks/yokes straight ahead', fontsize=10)
# ---------- top view (looking down the steering axis, slab t 90-160)
s = (Pf[:, 2] > 90) & (Pf[:, 2] < 160); bx.scatter(Pf[s, 0], Pf[s, 1], s=0.3, c='#999', lw=0)
s = (Pr[:, 2] > 90) & (Pr[:, 2] < 160); bx.scatter(Pr[s, 0], Pr[s, 1], s=0.3, c='#d9b3b3', lw=0)
s = (sw[:, 2] > 90) & (sw[:, 2] < 160); idx = np.random.default_rng(0).choice(np.nonzero(s)[0], 40000)
bx.scatter(sw[idx, 0], sw[idx, 1], s=0.2, c='#f3d6d6', lw=0, zorder=0)
bx.add_patch(Circle((0, 0), 71, fill=False, ls=':', ec='#c33'))
bx.text(0, 76, 'forks never come inside this (40° lock)', color='#c33', ha='center', fontsize=8)
for sg in [1, -1]:
    bx.plot([sg * 32, sg * 32], [100, 205], color=STEEL, lw=5, alpha=.7)
    hp = np.array([[33, 110], [42, 40], [45, 0], [35, -30], [12, -48.5]]) * [sg, 1]
    bx.plot(*hp.T, color=TUBE, lw=5, solid_capstyle='round')
bx.plot([-32, 32], [140, 140], 'k-', lw=2); bx.plot([-32, 32], [175, 175], 'k-', lw=2)
bx.add_patch(Polygon([[-8, 128], [8, 128], [8, 148], [-8, 148]], fc='#555', hatch='///', alpha=.8))
clt = np.array([[-44.5, -10.9], [44.5, -10.9], [44.5, -25.9], [10, -30], [10, -58.5], [-10, -58.5], [-10, -30], [-44.5, -25.9]])
bx.add_patch(Polygon(clt, fc=CL, alpha=.5, ec=CL)); bx.add_patch(Circle((0, 0), 25, fill=False, lw=2))
bx.plot([0, 0], [-58.5, -175], color=TOW, lw=3, ls='--'); bx.text(4, -170, 'to tower', color=TOW)
bx.set_aspect('equal'); bx.set_xlim(-140, 140); bx.set_ylim(-190, 230); bx.invert_yaxis(); bx.grid(alpha=.25)
bx.set_title('TOP VIEW down the steering axis (front at the BOTTOM), mm from axis', fontsize=10)
bx.set_xlabel('sideways'); bx.set_ylabel('back  <-->  front (u)')
fig.suptitle('"Factory" nav-tower mount concept: no welding, no holes. Sketch to scale on the scan, but positions are approximate (±5 mm) and the tank is NOT in the scan', fontsize=12)
fig.savefig('factory-mount-concept.png', dpi=80)
