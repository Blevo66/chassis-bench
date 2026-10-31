"""Plain 10 mm pin with a small head as a STEP (gmsh / OpenCASCADE): shaft 10.0 x 35, head 16 x 4, Z axis, head underside at z = 0."""
import gmsh
gmsh.initialize(); gmsh.option.setNumber('General.Terminal', 0); gmsh.model.add('pin')
occ = gmsh.model.occ
head = occ.addCylinder(0, 0, -4, 0, 0, 4, 8.0)
shaft = occ.addCylinder(0, 0, 0, 0, 0, 35, 5.0)
occ.fuse([(3, head)], [(3, shaft)]); occ.synchronize()
gmsh.write('pin-10x35-head.step'); gmsh.finalize()
