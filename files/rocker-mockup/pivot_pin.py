"""Printed mock pivot pin for the rocker's frame mount (40 mm wide mount), plus a 12 -> 10 sleeve for Joel's rocker pivot hole.
Pin prints lying on its side (D-flat on the bed) so the layers run along it - much stronger than printed standing up."""
import numpy as np, trimesh, manifold3d as m3
import design as DS
D_PIN, L_SHANK, HEAD_D, HEAD_T, FLAT = 9.8, 50.0, 18.0, 4.0, 0.6
pin = m3.Manifold.cylinder(L_SHANK, D_PIN/2, D_PIN/2, 96) + m3.Manifold.cylinder(HEAD_T, HEAD_D/2, HEAD_D/2, 96).translate((0, 0, -HEAD_T))
pin -= m3.Manifold.cube((40, 3.2, 3.2), True).translate((0, 0, L_SHANK - 4))                  # 3 mm cross hole for a split pin / zip tie
pin = pin.translate((0, 0, HEAD_T)).rotate((0, 90, 0))                                         # lay it down along X
mesh = pin.to_mesh(); tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
zmin = tm.bounds[0][2]
cut = m3.Manifold(m3.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32))) - m3.Manifold.cube((200, 200, 20), True).translate((0, 0, zmin - 10 + FLAT))
mesh = cut.to_mesh(); tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts)); tm.apply_translation(-tm.bounds[0])
sl = m3.Manifold.cylinder(30.0, 6.0, 6.0, 96) - m3.Manifold.cylinder(30.0, 5.05, 5.05, 96)          # 12 OD (into the rocker's 12.08 hole), 10.1 bore, 30 long
ms = sl.to_mesh(); ts = trimesh.Trimesh(np.asarray(ms.vert_properties)[:, :3], np.asarray(ms.tri_verts))
for t, n in ((tm, 'pivot-pin-10mm'), (ts, 'pivot-sleeve-12-to-10')):
    assert t.is_watertight; t.export(n + '.stl'); print(n, t.extents.round(1))
DS.write_3mf([('Pivot pin 10 mm', tm, (20, 20)), ('Sleeve 12 to 10', ts, (20 + 6, 60 + 6))], 'pivot-pin-10mm.3mf')
