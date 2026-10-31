"""Dimensioned drawing of the mock-up rocker, seen from the bike's RIGHT side (front of the bike to the right)."""
import math, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from geom import G, sweep, D2R, dist
o = json.load(open('rocker-B82-outline.json'))
R, D, S = np.array(o['R'], float), np.array(o['D'], float), np.array(o['S'], float)
out = np.array(o['rocker_outline_rocker_coords'])
P = sweep(); droop, bump = P[0], P[-1]
# put the rocker as it sits at full droop, in bike coords (origin swingarm pivot), then mirror for the right-side view
def place(q, p):
    c, s = math.cos(p['rang']), math.sin(p['rang'])
    q = np.atleast_2d(q); w = np.c_[q[:, 0]*c - q[:, 1]*s, q[:, 0]*s + q[:, 1]*c] + p['R']
    return np.c_[-w[:, 0], w[:, 1]]                     # right side: + x = forwards
dRS, dRD, dDS = dist(R, S), dist(R, D), dist(D, S)
aR = G['incl']
aD = math.degrees(math.acos((dRD**2 + dDS**2 - dRS**2)/(2*dRD*dDS)))
aS = 180 - aR - aD
info = {'pivot_to_dogbone': dRD, 'pivot_to_shock': dRS, 'dogbone_to_shock': dDS, 'angle_at_pivot': aR, 'angle_at_dogbone': aD, 'angle_at_shock': aS}
rows = []
for name, p in (('Full droop (shock 380)', droop), ('Full bump (shock 285)', bump)):
    w = {k: (-p[k][0], p[k][1]) for k in ('R', 'D', 'S', 'lug')}
    ang = math.degrees(math.atan2(w['R'][1] - w['D'][1], w['R'][0] - w['D'][0]))  # pivot->dogbone line, degrees below level going rearwards
    rows.append((name, p['th']/D2R, w, ang))
    info[name] = {k: [round(v, 1) for v in w[k]] for k in w} | {'pivot_to_dogbone_line_deg_below_level_rearwards': round(ang, 1), 'arm_deg': round(p['th']/D2R, 1)}
json.dump(info, open('rocker-B82-dims.json', 'w'), indent=1)

fig, ax = plt.subplots(figsize=(11, 11))
q = place(out, droop); ax.fill(q[:, 0], q[:, 1], color='#f3c9a6', ec='#c0601a', lw=1.5)
r, d, s = (place(v, droop)[0] for v in (R, D, S))
for c, nm in ((r, 'PIVOT\n(frame lower mount)'), (d, 'DOGBONE EYE'), (s, 'SHOCK BOLT M10')):
    ax.add_patch(plt.Circle(c, 5.2, fc='white', ec='k', lw=1)); ax.plot(*c, 'k+', ms=8)
ax.plot([r[0], d[0], s[0], r[0]], [r[1], d[1], s[1], r[1]], 'k--', lw=1)
def lab(a, b, txt, off):
    m = (a + b)/2; n = np.array([-(b - a)[1], (b - a)[0]]); n = n/np.linalg.norm(n)*off
    ax.annotate(txt, m + n, ha='center', va='center', fontsize=13, fontweight='bold', color='#1d4f91',
                bbox=dict(fc='white', ec='#1d4f91', boxstyle='round,pad=0.25'))
lab(r, d, f'{dRD:.1f}', -14); lab(r, s, f'{dRS:.1f}', 16); lab(d, s, f'{dDS:.1f}', -16)
def angl(at, a, b, txt, rad=26):
    u1 = math.degrees(math.atan2(*(a - at)[::-1])); u2 = math.degrees(math.atan2(*(b - at)[::-1]))
    t = np.radians(np.linspace(u1, u1 + ((u2 - u1 + 540) % 360 - 180), 40)); ax.plot(at[0] + rad*np.cos(t), at[1] + rad*np.sin(t), color='#9b1d20')
    mid = t[len(t)//2]; ax.annotate(txt, (at[0] + (rad + 14)*np.cos(mid), at[1] + (rad + 14)*np.sin(mid)), ha='center', va='center', fontsize=12, color='#9b1d20', fontweight='bold')
angl(r, d, s, f'{aR:.1f}°', 30); angl(d, r, s, f'{aD:.1f}°', 24); angl(s, r, d, f'{aS:.1f}°', 24)
ax.plot(0, 0, 'kx', ms=10); ax.annotate('swingarm pivot\n(0, 0)', (0, 0), xytext=(6, 8), fontsize=9)
ax.annotate('FRONT OF BIKE →', (-40, -138), fontsize=12, fontweight='bold')
ax.set_aspect('equal'); ax.grid(alpha=.3)
ax.set_title(f'Rocker B mock-up, seen from the RIGHT side, at full droop\n'
             f'Holes 10.4 mm (shock M10; pivot and dogbone placeholders). Bosses: pivot R17, dogbone R13, shock R12.5. Plate 16 mm.', fontsize=11)
t = []
for name, th, w, ang in rows:
    t.append(f"{name}, arm {th:.1f}°:  pivot {w['R'][0]:.1f}, {w['R'][1]:.1f}   dogbone eye {w['D'][0]:.1f}, {w['D'][1]:.1f}   "
             f"shock bolt {w['S'][0]:.1f}, {w['S'][1]:.1f}   arm lug {w['lug'][0]:.1f}, {w['lug'][1]:.1f}   pivot→dogbone {ang:.1f}° below level")
ax.text(0.01, -0.06, 'Positions from the swingarm pivot, mm (x + = forwards, y + = up), right-side view:\n' + '\n'.join(t),
        transform=ax.transAxes, va='top', fontsize=9, family='monospace')
plt.savefig('rocker-B82-dims-right-side.png', dpi=90, bbox_inches='tight')
print(json.dumps(info, indent=1))
