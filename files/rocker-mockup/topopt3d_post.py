"""Density -> smooth printable mesh (STL/3MF), holes and slot re-cut exactly, clearance check, pictures."""
import json, math, numpy as np, trimesh, manifold3d as m3
from skimage import measure
from scipy import ndimage
import design as DS
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely import affinity
g = json.load(open('topopt3d_grid.json')); rho = np.load('topopt3d_density.npy'); H = g['H']; lo = np.array(g['lo'])
full = np.concatenate([rho[:, :, ::-1], rho], axis=2)                  # mirror the half model
full = ndimage.zoom(full, 2, order=1)                                   # finer grid for a smoother surface
h = H/2
full = ndimage.gaussian_filter(full, 0.8)
pad = np.pad(full, 2)
v, f, _, _ = measure.marching_cubes(pad, 0.45, spacing=(h, h, h))
v = (v/h - 2 + 0.5)*h + np.array([lo[0], lo[1], -full.shape[2]*h/2])   # sample centres back to part coords (z centred)
tm = trimesh.Trimesh(v, f, process=True)
trimesh.smoothing.filter_taubin(tm, iterations=25)
tm = max(tm.split(only_watertight=False), key=lambda q: abs(q.volume))
trimesh.repair.fix_normals(tm)
if tm.volume < 0: tm.invert()
print('raw mesh watertight', tm.is_watertight, 'volume', round(tm.volume/1000, 1))
man = m3.Manifold(m3.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
# clip to Joel's envelope, then re-cut the holes and the dogbone slot exactly
env = trimesh.load('joel_rocker.stl')
envm = m3.Manifold(m3.Mesh(np.asarray(env.vertices, np.float32), np.asarray(env.faces, np.uint32)))
man = man ^ envm
for c, r in (((0.0, 0.0), 6.04), ((-57.3, -93.9), 5.09), ((-151.7, 17.6), 5.09)):
    man -= m3.Manifold.cylinder(40, r, r, 64).translate((c[0], c[1], -20))
mesh = man.to_mesh(); out = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)
print('watertight', out.is_watertight, 'volume cm3', round(out.volume/1000, 1), 'vs your block', round(env.volume/1000, 1),
      'steel kg', round(out.volume*7.85e-6, 2), 'Ti kg', round(out.volume*4.43e-6, 2))
out.export('rocker-generative.stl')
# clearance check: side silhouette against the arm and shock sweeps (in Joel's sketch frame)
p0 = DS.poses[0]
to_sk = lambda gm: affinity.scale(affinity.rotate(gm, p0['rang'], origin=(0, 0), use_radians=True), -1, 1, origin=(0, 0))
from shapely.geometry import Polygon
sil = unary_union([Polygon(out.vertices[t][:, :2]).buffer(0.01) for t in out.faces if Polygon(out.vertices[t][:, :2]).area > 1e-6])
print('gap to arm sweep', round(sil.distance(to_sk(DS.arm_sw)), 1), 'gap to shock sweep', round(sil.distance(to_sk(DS.shk_sw)), 1))
# a print plate for the Bambu (part laid flat on its side face)
o = out.copy(); o.apply_translation(-o.bounds[0] + [10, 10, 0]); o.export('rocker-generative-plate.stl')
DS.write_3mf([('Rocker generative', o, (0, 0))], 'rocker-generative.3mf')
# pictures
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig = plt.figure(figsize=(18, 9))
for k, (el, az, t) in enumerate(((90, -90, 'Side (right side of the bike, as your sketch)'), (28, -60, '3/4 view'))):
    ax = fig.add_subplot(1, 2, k + 1, projection='3d')
    tri = out.vertices[out.faces]; n = out.face_normals
    light = np.clip(n @ np.array([0.4, 0.5, 0.75]), 0, 1)*0.75 + 0.25
    pc = Poly3DCollection(tri, facecolors=np.c_[light*0.72, light*0.74, light*0.78, np.ones(len(light))], edgecolor='none')
    ax.add_collection3d(pc)
    b = out.bounds; ctr = b.mean(0); r = (b[1] - b[0]).max()/2
    ax.set_xlim(ctr[0] - r, ctr[0] + r); ax.set_ylim(ctr[1] - r, ctr[1] + r); ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.view_init(el, az); ax.set_axis_off(); ax.set_title(t)
plt.tight_layout(); plt.savefig('rocker-generative.png', dpi=80)
