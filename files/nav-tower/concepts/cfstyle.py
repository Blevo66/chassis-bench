import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Ellipse, Rectangle
from matplotlib.path import Path
from scipy.spatial import cKDTree
exec(open('concepts.py').read().split('CONCEPTS = []')[0])
LEAN = np.radians(40.0); d = np.array([np.sin(LEAN), np.cos(LEAN)]); n = np.array([-np.cos(LEAN), np.sin(LEAN)])
DC = np.array([60., 300.]); DH, DD, DW = 99., 53., 133.; BLEN, BW = 160., 240.
dash_a, dash_b = DC - d*DH/2, DC + d*DH/2
brd_a, brd_b = DC + d*(DH/2 + 10), DC + d*(DH/2 + 170); BC = (brd_a + brd_b)/2
T = lambda p: tuple(np.round(p, 1))
CARB = '#3b3b3e'; CARB2 = '#58585c'; FORGED = '#4a4a4a'; ALU = '#9aa0a6'; BRK = '#202020'
fig = plt.figure(figsize=(21, 13))
ax = fig.add_axes([0.01, 0.05, 0.40, 0.84]); fx = fig.add_axes([0.42, 0.05, 0.26, 0.84])
ax._side = True; REC.clear(); ctx_side(ax); ax.set_xlim(-130, 270); ax.set_ylim(20, 500)
# rear foot (same path as the checked mount: hugs the head box inside the fork tubes, to bosses A and B)
wishbone(ax)
# carbon side cheek (one each side), hollow moulded section, big lightening window
cheek = [(40, 158), (52, 148), (120, 150), (170, 170), (174, 268), T(brd_b - n*32), T(brd_b - n*4), T(brd_a - n*4),
         T(dash_b + n*6), T(dash_a + n*6), (22, 232), (28, 175)]
P(ax, cheek, CARB, 5, lw=1.6)
win = [(70, 196), (128, 200), (150, 250), (118, 262), (86, 245)]
P(ax, win, '#f4f4f4', 6, lw=1.2)
win2 = [T(DC + d*75 - n*22), T(DC + d*150 - n*22), T(DC + d*95 - n*70)]
P(ax, win2, '#f4f4f4', 6, lw=1.2)
# weave highlight stripes
for k in range(6): ax.plot([30 + k*22, 60 + k*22], [190 + k*8, 300 + k*16], color=CARB2, lw=1, zorder=6, alpha=.6)
# lamp pod (twin round LEDs side by side, cans visible from the side/back like the photo)
P(ax, [(120, 190), (172, 182), (172, 262), (118, 255)], BRK, 7)
ax.add_patch(Ellipse((178, 222), 14, 72, fc=LAMP, ec=K, zorder=8))
ax.add_patch(Circle((140, 222), 20, fc='#111', ec='#777', lw=2, zorder=8))
for a in np.linspace(0, 2*np.pi, 10, endpoint=False): ax.add_patch(Circle((140 + 15*np.cos(a), 222 + 15*np.sin(a)), 2.2, fc='#777', zorder=9))
# folded black alu bracket holding the dash
P(ax, [T(dash_a - n*DD - d*6), T(dash_b - n*DD + d*6), T(dash_b - n*(DD + 3) + d*6), T(dash_a - n*(DD + 3) - d*6)], BRK, 8)
P(ax, [T(dash_a), T(dash_b), T(dash_b - n*DD), T(dash_a - n*DD)], DASH, 7, alpha=.9)
# forged-carbon top cradle with 4 x M6 inserts, cheeseboard on it
P(ax, [T(brd_a - n*4), T(brd_b - n*4), T(brd_b - n*22), T(brd_a - n*22 + d*20)], FORGED, 8)
for p in [BC - d*50, BC + d*50]: ax.add_patch(Circle(T(p - n*10), 4, fc='orange', ec='k', zorder=10))
P(ax, [T(brd_a), T(brd_b), T(brd_b + n*4), T(brd_a + n*4)], ALU, 9)
ta, tb = BC - d*62.5 + n*16, BC + d*62.5 + n*16
P(ax, [T(ta), T(tb), T(tb + n*9), T(ta + n*9)], TAB, 10)
for p in [BC - d*45, BC + d*45]: ax.plot(*np.c_[p + n*4, p + n*16], color='k', lw=3, zorder=9)
# fasteners: silver button heads like the photo
for p in [(48, 160), (110, 156), (165, 178), (166, 258), T(brd_a - n*14 + d*8), T(brd_b - n*14 - d*8), (30, 220)]:
    ax.add_patch(Circle(p, 4.5, fc='#ddd', ec='k', lw=1, zorder=11))
ax.annotate('carbon side cheek (one each side)\nhollow moulded, big windows,\nsilver button-head bolts', (100, 170), (150, 80), fontsize=10, arrowprops=dict(arrowstyle='->'))
ax.annotate('rear feet to bosses A + B\n(same path as before, runs\ninside the fork tubes)', (-40, 110), (-125, 300), fontsize=10, arrowprops=dict(arrowstyle='->'))
ax.annotate('twin round LEDs side by side,\ncans on show from the side', (150, 240), (185, 150), fontsize=10, arrowprops=dict(arrowstyle='->'))
ax.annotate('dash pod on a folded\nblack alu bracket', T(DC - n*30), (200, 320), fontsize=10, color=DASH, zorder=20, arrowprops=dict(arrowstyle='->', color=DASH))
ax.annotate('forged-carbon top cradle,\n4 x M6 inserts (VESA 100)', T(BC - n*14), (222, 470), fontsize=10, color='#c06000', zorder=20, arrowprops=dict(arrowstyle='->', color='#c06000'))
ax.annotate('cheeseboard + Tab A9\n(or roadbook)', T(BC + n*20), (-110, 470), fontsize=10, color=TAB, arrowprops=dict(arrowstyle='->', color=TAB))
ax.text(-125, 30, 'SIDE (front ->). Red dashed = fork/bar sweep at 40° lock. Green A/B = your bosses.', fontsize=10, color='#444')
polys = [np.asarray(p, float) for p in REC]
Ssw = sw[np.abs(sw[:, 0]) < 100]; Q = np.c_[-Ssw[:, 1], Ssw[:, 2]]; Q = Q[(Q[:, 0] > 0) & (Q[:, 1] > 100)]
E = np.vstack([np.linspace(p[j], p[(j+1) % len(p)], 40) for p in polys for j in range(len(p))])
clr = cKDTree(Q).query(E)[0].min(); ov = any(Path(p).contains_points(Q).any() for p in polys); print('clear', round(clr, 1), ov)
# ---- front view
ctx_front(fx); fx.set_xlim(-140, 140); fx.set_ylim(20, 500); wishbone(fx, True)
zb0, zb1 = brd_a[1], brd_b[1]
for s in (-1, 1):
    P(fx, [(s*41, 150), (s*48, 150), (s*92, 185), (s*92, 268), (s*72, zb0 + 10), (s*72, zb1 - 20), (s*62, zb1 - 20), (s*62, zb0 + 10), (s*82, 268), (s*82, 190), (s*41, 165)], CARB, 5)
P(fx, [(-BW/2, zb0), (BW/2, zb0), (BW/2, zb1), (-BW/2, zb1)], ALU, 4)
P(fx, [(-72, zb0 + 10), (72, zb0 + 10), (72, zb1 - 20), (-72, zb1 - 20)], FORGED, 4.5)
P(fx, [(-82, 185), (82, 185), (82, 262), (-82, 262)], BRK, 6)
lamps_front(fx, 222, 70, 41)
fx.add_patch(Rectangle((-DW/2, dash_a[1]), DW, dash_b[1] - dash_a[1], fill=False, ec=DASH, lw=2, ls='--', zorder=9))
fx.text(0, dash_a[1] + 30, 'dash (behind)', ha='center', fontsize=8, color=DASH, zorder=10)
fx.text(-135, 30, 'FRONT. Cheeks ~185 apart at the lamps, ~82 apart\nwhere they pass the head tube. Board 240 wide.', fontsize=10, color='#444')
fig.text(0.70, 0.86, 'What I took from the Carbon Fox tower', fontsize=14, weight='bold', va='top')
fig.text(0.70, 0.83, '\n'.join([
 '- Open skeleton, not a fairing: two structural carbon',
 '  side cheeks do all the work, everything else bolts in.',
 '- Big lightening windows, chunky moulded edges.',
 '- Lamps as a separate pod hung between the cheeks,',
 '  backs on show (theirs look like 2 round LEDs).',
 '- Forged-carbon top cradle for the nav kit.',
 '- Folded black alu brackets + silver Torx button heads.',
 '- A rear "foot" channel that bolts to the frame.',
 '',
 'Changes for your bike:',
 '- Feet go to your 4 M8 bosses (A, B each side).',
 '- Lamps side by side (Baja style), not stacked.',
 '- Cradle carries the swappable cheeseboard.',
 '',
 'Moulds: each cheek is a 2-part printed mould',
 '(left and right mirror), cradle is 1 mould,',
 'lamp pod is bought lamps in a small carbon box.',
 '',
 f'Closest approach to the fork/bar sweep: ~{clr:.0f} mm',
 '(side view, scan ±5 mm, so treat as tight).',
 '',
 'GUESSES: everything about their part except the look',
 '(their site blocks me, so no sizes or specs).',
 'Shapes here are a sketch, not a final outline.']), fontsize=11.5, va='top', family='DejaVu Sans')
fig.text(0.01, 0.975, 'Nav tower, Carbon Fox style: open carbon skeleton on your 4 bosses, twin lamps, dash bracket, cheeseboard on top', fontsize=19, weight='bold', va='top')
fig.text(0.01, 0.94, 'To scale on your frame scan, with the real Tab A9 (211 x 125) and dash pod (133 x 99 x 53). Dash and board lean back 40° as before.', fontsize=11.5, va='top', color='#333')
fig.savefig('concepts/tower-cf-skeleton.png', dpi=72)
