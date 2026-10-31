import sys, os, numpy as np, trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots(); shp=r.OneShape()
out=sys.argv[2]; os.makedirs(out,exist_ok=True)
def mesh(shape):
    BRepMesh_IncrementalMesh(shape,0.25,False,0.3,True)
    V=[];F=[];o=0
    e=TopExp_Explorer(shape,TopAbs_FACE)
    while e.More():
        f=TopoDS.Face(e.Current()); loc=TopLoc_Location()
        t=BRep_Tool.Triangulation_s(f,loc)
        if t:
            tr=loc.Transformation(); n=t.NbNodes()
            for i in range(1,n+1):
                p=t.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            rev=f.Orientation()==TopAbs_REVERSED
            for i in range(1,t.NbTriangles()+1):
                a,b,c=t.Triangle(i).Get()
                F.append((o+a-1,o+c-1,o+b-1) if rev else (o+a-1,o+b-1,o+c-1))
            o+=n
        e.Next()
    return trimesh.Trimesh(np.array(V),np.array(F),process=True)
e=TopExp_Explorer(shp,TopAbs_SOLID); k=0
while e.More():
    m=mesh(e.Current()); k+=1
    fn=f"{out}/{k:03d}.stl"; m.export(fn); print(k,len(m.faces),m.extents.round(1).tolist(),m.centroid.round(1).tolist(),round(m.volume))
    e.Next()
