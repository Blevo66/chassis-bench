import sys,numpy as np,trimesh,json
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Solid
src,dst=sys.argv[1],sys.argv[2]; M=sys.argv[3] if len(sys.argv)>3 else None
m=trimesh.load(src)
if M: m.apply_transform(np.array(json.load(open(M))['scan_to_bike']))
sew=BRepBuilderAPI_Sewing(1e-3)
V=m.vertices
for f in m.faces:
  p=BRepBuilderAPI_MakePolygon(*[gp_Pnt(*map(float,V[i])) for i in f],True)
  fc=BRepBuilderAPI_MakeFace(p.Wire(),True)
  if fc.IsDone(): sew.Add(fc.Face())
sew.Perform(); sh=sew.SewedShape()
ex=TopExp_Explorer(sh,TopAbs_SHELL); shells=[]
while ex.More(): shells.append(TopoDS.Shell_s(ex.Current())); ex.Next()
print('shells',len(shells))
ms=BRepBuilderAPI_MakeSolid()
for s in shells: ms.Add(s)
sol=ms.Solid(); fx=ShapeFix_Solid(sol); fx.Perform(); sol=fx.Solid()
print('valid',BRepCheck_Analyzer(sol).IsValid())
w=STEPControl_Writer(); w.Transfer(sol,STEPControl_AsIs); w.Write(dst)
