import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Wedge
R = np.array([[1, 0, 0], [0, 0.8824, -0.4705], [0, 0.4705, 0.8824]]); p0 = np.array([2.6, -16.2, -9.4])
L2S = lambda P: p0 + np.asarray(P, float) @ R
Pf = L2S(np.load('Pf.npy')); Pr = L2S(np.load('Pr.npy'))
rng = np.random.default_rng(1); pf = Pf[rng.choice(len(Pf), 50000)]; pr = Pr[rng.choice(len(Pr), 50000)]
# GUESSED eye positions (scan coords: x fwd = -Y, z up), for a ~1.8 m rider; see notes
EYES = {'standing (attack position)': (-430, 1150, '#c0392b'), 'seated': (-600, 880, '#2471a3')}
TAB_C = np.array([75., 395.]); TAB_H = 125.   # Galaxy Tab A9 landscape: 125 mm deep along the slope
DASH_C = np.array([35., 300.]); DASH_H = 99.
def best_tilt(c):
    angs = [np.degrees(np.arctan2(c[1] - e[1], c[0] - e[0])) for e in EYES.values()]  # direction eye->display
    return angs
fig, ax = plt.subplots(figsize=(15, 13))
ax.scatter(-pr[:, 1], pr[:, 2], s=.4, c='#c9b0b0', lw=0); ax.scatter(-pf[:, 1], pf[:, 2], s=.4, c='#555', lw=0)
rows = []
for name, c, h, col in [('tablet', TAB_C, TAB_H, '#1a5fe0'), ('dash pod', DASH_C, DASH_H, '#19b36b')]:
    dirs = []
    for en, (ex, ez, ec) in EYES.items():
        v = c - [ex, ez]; d = np.linalg.norm(v); ang = np.degrees(np.arctan2(-v[1], v[0]))  # below horizontal
        dirs.append(v / d); rows.append((name, en, round(ang), round(d)))
        ax.plot([ex, c[0]], [ez, c[1]], color=ec, lw=1, ls=':')
    nrm = -(dirs[0] + dirs[1]); nrm /= np.linalg.norm(nrm)        # face normal = bisector toward the eyes
    face = np.array([-nrm[1], nrm[0]])                              # along the face
    a, b = c - face * h / 2, c + face * h / 2
    ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=7, solid_capstyle='butt', zorder=5)
    lean = np.degrees(np.arctan2(abs(face[0]), abs(face[1])))      # lean back from vertical
    off = [round(np.degrees(np.arccos(np.clip(-d @ nrm, -1, 1)))) for d in dirs]
    rows.append((name, 'face leans back from vertical', round(lean), f'off-square: standing {off[0]}°, seated {off[1]}°'))
    ax.text(c[0] + 25, c[1] + (12 if name == 'tablet' else -18), f'{name}: leans back ~{round(lean)}° from vertical', color=col, fontsize=12, weight='bold')
for en, (ex, ez, ec) in EYES.items():
    ax.add_patch(Circle((ex, ez), 14, fc=ec, ec='k')); ax.text(ex - 10, ez + 25, f'eye, {en}\n(GUESS)', color=ec, fontsize=11, ha='center')
    ax.plot([ex, ex + 420], [ez, ez], color=ec, lw=.8)
    for deg, ls in [(15, '-'), (45, '--'), (60, ':')]:
        r = 1000; ax.plot([ex, ex + r * np.cos(np.radians(deg))], [ez, ez - r * np.sin(np.radians(deg))], color=ec, lw=.6, ls=ls, alpha=.6)
    ax.text(ex + 400, ez - 400 * np.tan(np.radians(15)) + 6, '15°', color=ec, fontsize=9); ax.text(ex + 300, ez - 300 * np.tan(np.radians(45)) + 6, '45°', color=ec, fontsize=9)
    ax.text(ex + 220, ez - 220 * np.tan(np.radians(60)) + 6, '60° max', color=ec, fontsize=9)
ax.set_aspect('equal'); ax.set_xlim(-700, 300); ax.set_ylim(-50, 1300); ax.grid(alpha=.25)
ax.set_xlabel('mm, front of bike to the RIGHT (scan coordinates)'); ax.set_ylabel('mm up')
ax.set_title('Where the tablet and dash want to point: sight lines from guessed rider eye positions\n'
             'Human-factors guidance (FAA HFDS ch.5): screen centre 10-60° below horizontal (most comfortable ~15°), face square to the line of sight, never >45° off', fontsize=12)
txt = '\n'.join(f'{r[0]:9s} {r[1]:32s} {r[2]:>4}{"°" if isinstance(r[2], int) else ""}  {"" if len(r) < 4 else (str(r[3]) + (" mm away" if isinstance(r[3], int) else ""))}' for r in rows)
ax.text(-690, 10, txt, family='monospace', fontsize=10.5, va='bottom', bbox=dict(fc='white', ec='#999'))
plt.savefig('concepts/screen-angles.png', dpi=75, bbox_inches='tight')
for r in rows: print(r)
