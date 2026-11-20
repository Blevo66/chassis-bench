import sys, glob, os; sys.path.insert(0,'tw3'); from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
def dec(m, n): return m.simplify_quadric_decimation(face_count=n) if len(m.faces) > n else m
fr = dec(trimesh.load('tw3/xl125r-frame-clean.stl'), 30000)
steer = [dec(trimesh.load(f'tw3/{k}.stl'), 8000) for k in ['yoke-bottom','yoke-top','handlebar']]
for s in (1,-1):
    c = trimesh.creation.cylinder(radius=21.5, height=240, sections=32)
    T = np.eye(4); T[:3,:3] = np.c_[EX, -B, A] if False else np.c_[EX, np.cross(A, EX), A]; c.apply_transform(T)
    c.apply_translation(s*91*EX - 22*B + (84)*A); steer.append(c)
COL = {'neck_carbon':'#2b2b2e','cheek_L':'#2b2b2e','cheek_R':'#2b2b2e','bulkhead':'#2b2b2e','nose_cowl':'#2b2b2e',
       'lamp_housings':'#151515','lamp_lenses':'#ffe9a8','dash_pod_placeholder':'#2c7a4b','dash_bracket_alu':'#1a1a1a','top_cradle_forged':'#4a4a4c',
       'cheeseboard_alu':'#b9bfc6','tablet_tab_a9_placeholder':'#1a3d8f','visor_polycarb':'#5f6f7a','button_heads_ti':'#d8d8d8'}
def sub(m, sz=6.0):
    v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=sz, max_iter=12); return trimesh.Trimesh(v, f, process=False)
tower = {k: sub(trimesh.load(f'tw3/out3/{k}.stl')) for k in COL}
steer = [sub(m, 12) for m in steer]
def view(ax, az, el, items, xlim=None, ylim=None, title=''):
    a, e = np.radians(az), np.radians(el)
    # camera: looking direction from azimuth (0 = from front, i.e. camera at -Y), elevation
    cam = np.array([np.sin(a)*np.cos(e), -np.cos(a)*np.cos(e), np.sin(e)])   # camera position direction
    right = np.cross([0,0,1], cam); right /= np.linalg.norm(right); up = np.cross(cam, right)
    L = np.array([0.4, -0.6, 0.7]); L /= np.linalg.norm(L)
    polys, cols, depth = [], [], []
    for m, col, alpha in items:
        tri = m.vertices[m.faces]; nrm = m.face_normals
        vis = np.ones(len(tri), bool)
        P = np.stack([tri @ right, tri @ up], -1); dpt = (tri @ cam).mean(1)
        sh = 0.35 + 0.65*np.abs(nrm @ L)
        base = np.array(matplotlib.colors.to_rgb(col))
        c = np.clip(base[None]*sh[:,None] + 0.08*(sh[:,None]**8), 0, 1)
        polys.append(P[vis]); cols.append(np.c_[c[vis], np.full(vis.sum(), alpha)]); depth.append(dpt[vis])
    P = np.concatenate(polys); C = np.concatenate(cols); D = np.concatenate(depth); o = np.argsort(D)
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors=C[o], linewidths=0.15))
    ax.set_aspect('equal'); ax.autoscale_view()
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    ax.axis('off'); ax.set_title(title, fontsize=14)
items = [(fr, '#b23a3a', 1)] + [(m, '#c8c8c8', 1) for m in steer] + [(m, COL[k], .55 if k=='visor_polycarb' else 1) for k, m in tower.items()]
fig = plt.figure(figsize=(22, 16))
ax = fig.add_axes([0.0, 0.40, 0.5, 0.56]); view(ax, -35, 15, items, (-420, 330), (-170, 520), 'front three-quarter')
ax = fig.add_axes([0.5, 0.40, 0.5, 0.56]); view(ax, 145, 28, items, (-380, 380), (-200, 560), 'rider\'s view (rear three-quarter)')
ax = fig.add_axes([0.0, 0.0, 0.42, 0.40]); view(ax, 90, 0, items, (-260, 420), (-180, 520), 'right side')
ax = fig.add_axes([0.42, 0.0, 0.30, 0.40]); view(ax, 0, 0, items, (-260, 260), (-180, 520), 'front')
ax = fig.add_axes([0.72, 0.0, 0.28, 0.40]); view(ax, 0, 89, items, (-260, 260), (-330, 330), 'from above')
fig.savefig('tw3/out3/tower-v3-renders.png', dpi=60)
# hero close-up
fig = plt.figure(figsize=(14, 14)); ax = fig.add_axes([0, 0, 1, 1])
view(ax, -40, 18, [(fr, '#b23a3a', 1)] + [(m, '#c8c8c8', 1) for m in steer] + [(m, COL[k], .55 if k=='visor_polycarb' else 1) for k, m in tower.items()], (-300, 280), (-60, 520))
fig.savefig('tw3/out3/tower-v3-hero.png', dpi=70)
