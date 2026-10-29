"""Turn the raw Scaniverse frame scan into Fusion-ready meshes.

python3 make_fusion_scan.py scan.stl
Needs: trimesh, numpy, pymeshlab. Writes xl125r-frame-scan-full.stl and -light.stl/.obj.

Steps: metres -> mm, cut away the stand plank (plane fitted to it, +16 mm),
move the swingarm pivot to the origin, axes X forward / Y left / Z up,
scale x0.969 and rotate 12.4 deg about the pivot axis so the top shock
mount lands 55 mm ahead and 292 mm up (Joel's tape), close holes, then
decimate to ~9k triangles for Fusion's Convert Mesh.
"""
import sys, numpy as np, trimesh, pymeshlab as ml

SRC = sys.argv[1]
PIVOT = np.array([-18.0, 983.7, 173.8])   # scan mm (x, y up, z rearward); x = mid of the pivot plates
SCALE, TILT = 0.969, -12.4
PLANK = (854.75, 0.11365, 0.01532)        # stand top: y = a + b*z + c*x, scan mm

m = trimesh.load(SRC); m.apply_scale(1000)
v = m.vertices
plank = PLANK[0] + PLANK[1] * v[:, 2] + PLANK[2] * v[:, 0]
bridge = (v[:, 1] < 928) & (np.abs(v[:, 0] - PIVOT[0]) < 100) & (v[:, 2] > 110) & (v[:, 2] < 330)
bad = (v[:, 1] < plank + 16) | bridge     # plank, and the plank lip melted between the pivot plates
m.update_faces(~bad[m.faces].any(1)); m.remove_unreferenced_vertices()
m = trimesh.util.concatenate([c for c in m.split(only_watertight=False) if len(c.faces) > 300])

p = m.vertices - PIVOT
q = np.c_[-p[:, 2], -p[:, 0], p[:, 1]] * SCALE
c, s = np.cos(np.radians(TILT)), np.sin(np.radians(TILT))
m.vertices = np.c_[c * q[:, 0] + s * q[:, 2], q[:, 1], -s * q[:, 0] + c * q[:, 2]]

ms = ml.MeshSet(); ms.add_mesh(ml.Mesh(m.vertices, m.faces))
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_duplicate_faces(); ms.meshing_remove_null_faces()
for _ in range(2):
    ms.meshing_repair_non_manifold_edges(method=0); ms.meshing_repair_non_manifold_vertices()
    ms.meshing_close_holes(maxholesize=300, newfaceselected=False)
mm = ms.current_mesh(); full = trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix())
parts = full.split(only_watertight=False)
for part in parts: part.fix_normals()
trimesh.util.concatenate(parts).export('xl125r-frame-scan-full.stl')

light = []
for part in parts:
    ms = ml.MeshSet(); ms.add_mesh(ml.Mesh(part.vertices, part.faces))
    ms.apply_coord_taubin_smoothing(stepsmoothnum=6)
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=max(200, len(part.faces) * 9000 // 36446),
        preservetopology=True, preservenormal=True, preserveboundary=True, qualitythr=0.4, planarquadric=True)
    mm = ms.current_mesh(); x = trimesh.Trimesh(mm.vertex_matrix(), mm.face_matrix()); x.fix_normals()
    light.append(x)
light = trimesh.util.concatenate(light)
light.export('xl125r-frame-scan-light.stl'); light.export('xl125r-frame-scan-light.obj')
print(len(full.faces), len(light.faces), light.is_watertight)
