import sys,numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopoDS import TopoDS
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import trimesh
r=STEPControl_Reader();r.ReadFile(sys.argv[1]);r.TransferRoots();s=r.OneShape()
BRepMesh_IncrementalMesh(s,0.2,False,0.2,True)
V=[];F=[];cyl=[]
ex=TopExp_Explorer(s,TopAbs_FACE)
while ex.More():
  f=TopoDS.Face(ex.Current());loc=TopLoc_Location()
  tri=BRep_Tool.Triangulation_s(f,loc)
  if tri:
    tr=loc.Transformation();o=len(V)
    for i in range(1,tri.NbNodes()+1):
      p=tri.Node(i).Transformed(tr);V.append([p.X(),p.Y(),p.Z()])
    for i in range(1,tri.NbTriangles()+1):
      a,b,c=tri.Triangle(i).Get();F.append([o+a-1,o+b-1,o+c-1])
  ad=BRepAdaptor_Surface(f)
  if ad.GetType()==GeomAbs_Cylinder:
    c=ad.Cylinder();ax=c.Axis();l=ax.Location();dd=ax.Direction()
    g=GProp_GProps();BRepGProp.SurfaceProperties_s(f,g)
    cyl.append((round(c.Radius(),2),[round(l.X(),2),round(l.Y(),2),round(l.Z(),2)],[round(dd.X(),3),round(dd.Y(),3),round(dd.Z(),3)],round(g.Mass(),0)))
  ex.Next()
m=trimesh.Trimesh(np.array(V),np.array(F));m.merge_vertices()
print('bounds',m.bounds.round(2),'watertight',m.is_watertight,'vol',round(m.volume))
m.export('clamp_raw.stl')
seen=set()
for c in sorted(cyl):
  k=(c[0],tuple(c[2]),tuple(np.round(c[1],0)))
  if k in seen: continue
  seen.add(k);print('cyl r',c[0],'pt',c[1],'dir',c[2],'area',c[3])
