"""Render the slim front pair + rear side tanks on the frame scan. python3 render_rear.py REARDIR FRONTDIR"""
import sys, pickle, numpy as np, trimesh, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
RD, FD = sys.argv[1], sys.argv[2]
fv = trimesh.load('/mnt/project-files/frame-scan/fusion/xl125r-frame-scan-full.stl').vertices
F = [trimesh.load(f'{FD}/tank-{s}-half.stl') for s in ('left', 'right')]
B = [trimesh.load(f'{RD}/rear-tank-{s}.stl') for s in ('left', 'right')]
# rear tyre at full bump (axle ~580 back, ~20 up) and full droop (20 deg), 4.10-18 ~ r 323
tyre = [(-580 * np.cos(np.radians(a)), -580 * np.sin(np.radians(a))) for a in (-2, 20)]
def edges(m): return m.vertices[m.face_adjacency_edges[np.degrees(m.face_adjacency_angles) > 3]]
def shade(m, v, base):
    k = np.clip(m.face_normals @ (np.array(v) / np.linalg.norm(v)), 0, 1)
    return [tuple(np.clip(np.array(base) * (0.6 + 0.45 * x), 0, 1)) for x in k]
fig = plt.figure(figsize=(18, 9))
for i, (el, az) in enumerate(((16, -40), (14, -140))):
    a = fig.add_subplot(1, 2, i + 1, projection='3d')
    for ms, col in ((F, (.62, .66, .7)), (B, (.75, .62, .45))):
        for m in ms:
            a.add_collection3d(Poly3DCollection(m.triangles, facecolors=shade(m, [np.cos(np.radians(az)), np.sin(np.radians(az)), 1.2], col), edgecolor='none'))
            a.add_collection3d(Line3DCollection(edges(m), colors='#222', lw=.7))
    a.scatter(fv[::2, 0], fv[::2, 1], fv[::2, 2], s=.15, c='0.35')
    t = np.linspace(0, 2 * np.pi, 90); cx, cz = tyre[0]
    for y in (-55, 55): a.plot(cx + 323 * np.cos(t), y + 0 * t, cz + 323 * np.sin(t), c='0.6', lw=.8)
    a.set_xlim(-650, 500); a.set_ylim(-575, 575); a.set_zlim(-150, 650); a.set_box_aspect((1150, 1150, 800)); a.view_init(el, az); a.set_axis_off()
plt.tight_layout(); plt.savefig(f'{RD}/front-plus-rear-3d.png', dpi=75)
fig, ax = plt.subplots(1, 2, figsize=(20, 8), gridspec_kw={'width_ratios': [2.3, 1]})
ax[0].scatter(fv[:, 0], fv[:, 2], s=.05, c='0.45')
for ms, c in ((F, 'k'), (B, '#b0601a')):
    for p in edges(ms[0]): ax[0].plot(p[:, 0], p[:, 2], c, lw=.6)
t = np.linspace(0, 2 * np.pi, 120)
for (cx, cz), ls, lab in ((tyre[0], '-', 'tyre at full bump'), (tyre[1], ':', 'tyre at full droop')):
    ax[0].plot(cx + 323 * np.cos(t), cz + 323 * np.sin(t), c='0.55', ls=ls, lw=1, label=lab)
ax[0].plot([0, tyre[0][0]], [0, tyre[0][1]], c='0.55', lw=2)
ax[0].axhline(0, c='0.8', lw=.5); ax[0].legend(loc='lower right')
ax[0].set_aspect('equal'); ax[0].grid(alpha=.3); ax[0].set_xlim(-920, 560); ax[0].set_ylim(-540, 640)
ax[0].set_title('Side view, left. Grey = slim front pair, orange = rear side tank. mm from swingarm pivot')
s = fv[:, 0] < 450; ax[1].scatter(fv[s, 1], fv[s, 0], s=.05, c='0.45')
for ms, c in ((F, 'k'), (B, '#b0601a')):
    for m in ms:
        for p in edges(m): ax[1].plot(p[:, 1], p[:, 0], c, lw=.5)
ax[1].add_patch(plt.Rectangle((-55, -900), 110, 650, fc='0.9', ec='0.6')); ax[1].text(0, -600, 'tyre', ha='center', rotation=90, color='0.5')
ax[1].invert_xaxis(); ax[1].set_aspect('equal'); ax[1].grid(alpha=.3); ax[1].set_title('Top view, front at top'); ax[1].set_ylim(-920, 400)
plt.tight_layout(); plt.savefig(f'{RD}/front-plus-rear-views.png', dpi=75)
fl = pickle.load(open(f'{RD}/.rflats.pkl', 'rb'))
fig, axs = plt.subplots(2, 4, figsize=(20, 9)); axs = axs.ravel()
for a, (n, f) in zip(axs, fl.items()):
    x, y = f[0].exterior.xy; a.plot(x, y, 'r', lw=1.2)
    for p, q, an, kd in f[1]:
        if an >= 3: a.plot([p[0], q[0]], [p[1], q[1]], 'b--' if kd == 'out' else 'g--', lw=.7)
    a.set_aspect('equal'); a.grid(alpha=.3); a.set_title(n)
for a in axs[len(fl):]: a.axis('off')
fig.suptitle('Rear tank flats (LEFT, mirror for right). Red = cut, blue dashed = fold out, green = fold IN')
plt.tight_layout(); plt.savefig(f'{RD}/rear-flat-patterns.png', dpi=65)
