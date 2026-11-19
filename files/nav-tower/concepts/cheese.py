import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse, Rectangle, FancyBboxPatch
from matplotlib.path import Path
from scipy.spatial import cKDTree
exec(open('concepts.py').read().split('CONCEPTS = []')[0])
LEAN = 40.0; L = np.radians(LEAN)
d = np.array([np.sin(L), np.cos(L)]); n = np.array([-np.cos(L), np.sin(L)])   # up-the-face, face normal (toward rider)
DC = np.array([55., 300.]); DH, DD, DW = 99., 53., 133.
BS0, BLEN, BW, BT = DH/2 + 10, 160., 240., 4.    # board starts 10 above dash top, 160 long along the slope, 240 wide
def seg(c, s0, s1): return c + d * s0, c + d * s1
dash_a, dash_b = seg(DC, -DH/2, DH/2)
brd_a, brd_b = seg(DC, BS0, BS0 + BLEN); BC = (brd_a + brd_b) / 2
EYES = {'standing': (-430, 1150, '#c0392b'), 'seated': (-600, 880, '#2471a3')}
rep = []
for nm, c in [('dash', DC), ('tablet/roadbook (board centre)', BC + n * 12)]:
    for en, (ex, ez, _) in EYES.items():
        v = np.array([ex, ez]) - c; dist = np.linalg.norm(v); below = np.degrees(np.arctan2(v[1], -v[0]))
        off = np.degrees(np.arccos(v @ n / dist)); rep.append(f'{nm:30s} {en:8s}: {below:4.0f}° below eye line, {off:3.0f}° off square, {dist:4.0f} mm away')
print('\n'.join(rep))
fig = plt.figure(figsize=(21, 13))
ax = fig.add_axes([0.01, 0.05, 0.36, 0.83]); fx = fig.add_axes([0.37, 0.05, 0.25, 0.83]); bx = fig.add_axes([0.64, 0.30, 0.35, 0.55])
ax._side = True; REC.clear()
ctx_side(ax); ax.set_xlim(-130, 260); ax.set_ylim(20, 500)
wishbone(ax)
# body: lamp nose + neck up to the sloped face
body = [(52, 150), (150, 160), (160, 175), (150, 262), dash_a + d*0 - n*0 + np.array([0, 0]), ]
dashbox = [dash_a, dash_b, dash_b - n*DD, dash_a - n*DD]
top_deck = [brd_a - n*3, brd_b - n*3, brd_b - n*28, brd_a - n*45]
P(ax, [(40, 160), (52, 150), (150, 160), (160, 175), (152, 262), tuple(brd_b - n*30), tuple(brd_b - n*3), tuple(brd_a - n*3), tuple(dash_b), tuple(dash_a), (25, 230)], WH, 5)
P(ax, [(150, 160), (160, 175), (150, 205), (55, 190), (52, 150)], CF, 6)
P(ax, [(152, 214), (143, 238), (60, 228), (58, 210)], RED, 6, ec='none'); P(ax, [(141, 244), (136, 258), (62, 248), (61, 236)], BLU, 6, ec='none')
lamps_side(ax, 150, 222, 70)
P(ax, [tuple(p) for p in dashbox], DASH, 7, alpha=.9)
P(ax, [(150, 262), (175, 250), tuple(brd_b - n*30 + d*0), tuple(brd_b - n*45)], GLASS, 4, alpha=.0)
# board + tablet (solid) + roadbook (dashed outline)
P(ax, [tuple(brd_a), tuple(brd_b), tuple(brd_b + n*BT), tuple(brd_a + n*BT)], '#9aa3ad', 8)
ta, tb = BC - d*62.5 + n*(BT+12), BC + d*62.5 + n*(BT+12)
P(ax, [tuple(ta), tuple(tb), tuple(tb + n*9), tuple(ta + n*9)], TAB, 9)
for p in [BC - d*45, BC + d*45]: ax.plot(*np.c_[p, p + n*(BT+12)], color='k', lw=3, zorder=8)
rb = [BC - d*85 + n*BT, BC + d*85 + n*BT, BC + d*85 + n*55, BC - d*85 + n*55]
ax.add_patch(Polygon(rb, fill=False, ec='#8e44ad', lw=1.8, ls='--', zorder=9))
for p in [BC - d*50, BC + d*50]: ax.add_patch(Circle(tuple(p - n*6), 4, fc='orange', ec='k', zorder=10))
for en, (ex, ez, ec) in EYES.items():
    for tgt in (DC, BC): ax.plot([tgt[0], tgt[0] + (ex - tgt[0]) * .35], [tgt[1], tgt[1] + (ez - tgt[1]) * .35], ':', color=ec, lw=1.2, zorder=11)
ax.annotate('to eye, standing', (DC[0] + (EYES['standing'][0]-DC[0])*.3, DC[1] + (EYES['standing'][1]-DC[1])*.3), fontsize=9, color='#c0392b')
ax.annotate('to eye, seated', (BC[0] + (EYES['seated'][0]-BC[0])*.33, BC[1] + (EYES['seated'][1]-BC[1])*.33 - 10), fontsize=9, color='#2471a3')
ax.annotate('cheeseboard, 4 mm alu\n240 x 160, swaps tablet <-> roadbook', tuple(brd_b + n*2), (150, 485), fontsize=10, arrowprops=dict(arrowstyle='->'))
ax.annotate('Tab A9 in its holder', tuple(BC + n*20), (-120, 470), color=TAB, fontsize=10, arrowprops=dict(arrowstyle='->', color=TAB))
ax.annotate('roadbook holder\n(purple dashed, size GUESS)', tuple(rb[3]), (-125, 420), color='#8e44ad', fontsize=10, arrowprops=dict(arrowstyle='->', color='#8e44ad'))
ax.annotate('4 x M6 bonded inserts\n+ rubber isolators', tuple(BC - d*50 - n*6), (200, 380), color="#c06000", fontsize=10, arrowprops=dict(arrowstyle='->', color='#c06000'))
ax.annotate('dash pod 133 x 99 x 53\nfixed to the tower,\nleaning back 40°', tuple(DC - n*25), (185, 300), color=DASH, fontsize=10, arrowprops=dict(arrowstyle='->', color=DASH))
ax.text(-125, 30, 'SIDE (front ->). Red dashed = fork/bar sweep at 40° lock. Green A/B = your bosses.', fontsize=10, color='#444')
# clearance check
side_polys = [np.asarray(p, float) for p in REC]
hw = BW/2 + 5; Ssw = sw[np.abs(sw[:, 0]) < hw]; Q = np.c_[-Ssw[:, 1], Ssw[:, 2]]; Q = Q[(Q[:, 0] > 0) & (Q[:, 1] > 100)]
E = np.vstack([np.linspace(p[j], p[(j+1) % len(p)], 40) for p in side_polys for j in range(len(p))])
clr = cKDTree(Q).query(E)[0].min(); ov = any(Path(p).contains_points(Q).any() for p in side_polys)
print('sweep clearance', round(clr, 1), 'overlap' if ov else 'clear')
# front view
ctx_front(fx); fx.set_xlim(-140, 140); fx.set_ylim(20, 500); wishbone(fx, True)
P(fx, [(-88, 160), (88, 160), (95, 255), (72, 300), (70, DC[1] + 50), (-70, DC[1] + 50), (-72, 300), (-95, 255)], WH, 5)
P(fx, [(-88, 160), (88, 160), (80, 190), (-80, 190)], CF, 6)
P(fx, [(-95, 255), (95, 255), (92, 262), (-92, 262)], RED, 6, ec='none')
lamps_front(fx, 222, 70, 44)
zb0, zb1 = brd_a[1], brd_b[1]
P(fx, [(-BW/2, zb0), (BW/2, zb0), (BW/2, zb1), (-BW/2, zb1)], '#9aa3ad', 4)
P(fx, [(-75, zb0 - 2), (75, zb0 - 2), (60, zb1 - 15), (-60, zb1 - 15)], WH, 5)
fx.add_patch(Rectangle((-DW/2, dash_a[1] - 6), DW, dash_b[1] - dash_a[1] + 6, fill=False, ec=DASH, lw=2, ls='--', zorder=9))
fx.text(0, dash_a[1] + 25, 'dash\n(behind,\nfaces rider)', ha='center', fontsize=8, color=DASH, zorder=10)
fx.text(-135, 30, 'FRONT. Board is the widest bit (240);\nlamp nose ~190, dash 133.', fontsize=10, color='#444')
# board detail (looking at the face)
bx.set_aspect('equal'); bx.set_xlim(-135, 135); bx.set_ylim(-95, 95); bx.axis('off')
bx.add_patch(FancyBboxPatch((-BW/2, -BLEN/2), BW, BLEN, boxstyle='round,pad=0,rounding_size=10', fc='#c8ced4', ec='k', lw=1.5))
gx = np.arange(-100, 101, 20); gy = np.arange(-60, 61, 20)
for x in gx:
    for y in gy: bx.add_patch(Circle((x, y), 3.25, fc='w', ec='#555', lw=.6))
bx.add_patch(Rectangle((-105.5, -62.5), 211, 125, fill=False, ec=TAB, lw=2.5))
bx.text(0, 50, 'Galaxy Tab A9 landscape 211 x 125', ha='center', color=TAB, fontsize=10, weight='bold')
bx.add_patch(Rectangle((-95, -85), 190, 170, fill=False, ec='#8e44ad', lw=2, ls='--'))
bx.text(0, -80, 'typical roadbook holder footprint ~190 x 170 (GUESS)', ha='center', color='#8e44ad', fontsize=9)
for x, y in [(-50, -50), (50, -50), (-50, 50), (50, 50)]:
    bx.add_patch(Circle((x, y), 6, fc='orange', ec='k', zorder=5))
bx.text(0, -8, '4 tower mounting points, 100 x 100 square\n(VESA 100, so off-the-shelf tablet/phone\nholders bolt straight on too)', ha='center', fontsize=9.5, color='#c06000')
bx.set_title('Cheeseboard, looking at its face: 4 mm 6082 alu, 6.5 mm holes on a 20 mm grid', fontsize=11)
txt = 'Viewing angles (eye positions are GUESSES for a ~1.8 m rider; send me yours):\n' + '\n'.join(rep) + \
      f'\nClosest approach of tower/board to the 40° lock sweep (side view, ±{hw:.0f} mm wide): {clr:.0f} mm'
fig.text(0.64, 0.05, txt, family='monospace', fontsize=9.3, va='bottom')
fig.text(0.01, 0.975, 'Nav tower with a bolt-on cheeseboard: lamps + dash on the tower, tablet OR roadbook on a swappable plate on top', fontsize=19, weight='bold', va='top')
fig.text(0.01, 0.94, 'To scale on your frame scan. Shell drawn in the "modern Dakar" style just as a placeholder: any of the 4 concept shells can wrap the same layout. Real Tab A9 (211 x 125 x 8) and dash pod (133 x 99 x 53).', fontsize=11.5, va='top', color='#333')
fig.savefig('concepts/tower-cheeseboard.png', dpi=72)
