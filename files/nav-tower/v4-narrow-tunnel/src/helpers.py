import sys, json; sys.path.insert(0, 'tw3'); from common import *
from shapely.geometry import Polygon as SP, LineString
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepTools import BRepTools
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt
P3 = lambda p: gp_Pnt(*map(float, p))
def chaikin(P, n=4, closed=True):
    P = np.asarray(P, float)
    for _ in range(n):
        Q = []
        for i in range(len(P) if closed else len(P) - 1):
            a, b = P[i], P[(i + 1) % len(P)]; Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        P = np.array(Q)
    return P
def spline_wire(pts3):
    arr = TColgp_HArray1OfPnt(1, len(pts3))
    for i, p in enumerate(pts3): arr.SetValue(i + 1, P3(p))
    it = GeomAPI_Interpolate(arr, True, 1e-6); it.Perform()
    return BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(it.Curve()).Edge()).Wire()
def prism(pts3, vec, smooth=False):
    if smooth: w = spline_wire(pts3)
    else:
        mp = BRepBuilderAPI_MakePolygon()
        for p in pts3: mp.Add(P3(p))
        mp.Close(); w = mp.Wire()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w).Face(), gp_Vec(*map(float, vec))).Shape()
def cyl(c, axis, r, h):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(P3(c), gp_Dir(*axis)), float(r), float(h)).Shape()
cut = lambda a, b: BRepAlgoAPI_Cut(a, b).Shape(); fuse = lambda a, b: BRepAlgoAPI_Fuse(a, b).Shape()
def fillet(s, r):
    try:
        mk = BRepFilletAPI_MakeFillet(s); ex = TopExp_Explorer(s, TopAbs_EDGE)
        while ex.More(): mk.Add(float(r), TopoDS.Edge(ex.Current())); ex.Next()
        mk.Build()
        return mk.Shape() if mk.IsDone() else s
    except Exception as e: print('fillet failed', e); return s
W = lambda f, z, x=0.0: np.array([x, -f, z], float)
loc = lambda v, u, t: v * EX + u * B + t * A
def round_poly(p, r_out, r_in=None):
    p = SP(p).buffer(0); p = p.buffer(-r_out, join_style=1).buffer(r_out, join_style=1)
    if r_in: p = p.buffer(r_in, join_style=1).buffer(-r_in, join_style=1)
    return p
def ring(poly, step=4.0):
    c = np.array(poly.exterior.coords)[:-1]; L = LineString(np.vstack([c, c[:1]]))
    k = max(24, int(L.length / step)); return np.array([L.interpolate(i / k, normalized=True).coords[0] for i in range(k)])
def side_part(poly2, x0, dx, smooth=True):
    pts = ring(poly2, 6.0) if smooth else np.asarray(poly2)
    return prism([W(f, z, x0) for f, z in pts], (dx, 0, 0), smooth=False)
