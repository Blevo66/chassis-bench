"""Preview images: side view against the frame scan and tyre, plus a 3D view of the 3 parts."""
import sys, os, numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import make_rear_mudguard as M
D = sys.argv[1]; SCAN = sys.argv[2]
P = [trimesh.load(os.path.join(D, f'rear-mudguard-part{i}.stl')) for i in (1, 2, 3)]
cols = ['#c8102e', '#e8e8e8', '#1f4e9c']
scan = trimesh.load(SCAN).vertices
fig, ax = plt.subplots(figsize=(13, 7))
r = scan[scan[:, 0] < 120]
ax.scatter(r[:, 0], r[:, 2], s=0.2, c='#999', label='frame scan')
th = np.linspace(0, 2 * np.pi, 300)
for ang, ls, lab in [(M.BUMP, '-', 'tyre at full bump'), (M.DROOP, ':', 'tyre at full droop')]:
    a = np.array([-M.ARM * np.cos(np.radians(ang)), M.ARM * np.sin(np.radians(ang))])
    ax.plot(a[0] + M.TYRE_R * np.cos(th), a[1] + M.TYRE_R * np.sin(th), 'k', ls=ls, lw=1, label=lab)
    ax.plot([0, a[0]], [0, a[1]], color='#555', ls=ls, lw=3)
for p, c in zip(P, cols):
    s = p.vertices; ax.scatter(s[:, 0], s[:, 2], s=0.4, c=c)
ax.plot([M.TAB_X], [M.TAB_Z], 'o', ms=10, mfc='none', mec='g', mew=2, label='side tab M6 (slotted)')
ax.plot([M.CROSS_X], [338], 's', ms=9, mfc='none', mec='m', mew=2, label='P-clip to cross-member')
ax.set_aspect('equal'); ax.set_xlim(-960, 150); ax.set_ylim(-260, 470); ax.grid(alpha=.3)
ax.set_title('Rear mudguard, left side view (mm from swingarm pivot). Red / white / blue = parts 1 / 2 / 3')
ax.legend(loc='lower left', fontsize=8); plt.tight_layout(); plt.savefig(os.path.join(D, 'rear-mudguard-side.png'), dpi=90)

fig = plt.figure(figsize=(12, 7)); ax = fig.add_subplot(111, projection='3d')
for p, c in zip(P, cols):
    q = p.simplify_quadric_decimation(face_count=5000) if len(p.faces) > 3000 else p
    pc = Poly3DCollection(q.vertices[q.faces], facecolor=c, edgecolor='#333', linewidths=0.05, alpha=1)
    n = q.face_normals; sh = 0.55 + 0.45 * np.clip(n @ np.array([0.3, 0.5, 0.8]), 0, 1)
    base = np.array(matplotlib.colors.to_rgb(c)); pc.set_facecolor(np.clip(base[None] * sh[:, None], 0, 1))
    ax.add_collection3d(pc)
ax.set_xlim(-780, -190); ax.set_ylim(-150, 150); ax.set_zlim(270, 430)
ax.set_box_aspect((590, 300, 160), zoom=1.0); ax.view_init(30, -135); ax.set_axis_off()
ax.set_title('Rear mudguard, 3 parts, seen from behind and to the right (red is the front)')
plt.tight_layout(); plt.savefig(os.path.join(D, 'rear-mudguard-3d.png'), dpi=90)
