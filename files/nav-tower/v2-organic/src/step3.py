import glob, os
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TDataStd import TDataStd_Name
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
import matplotlib.colors as mc
COL = {'neck_carbon':'#2b2b2e','cheek_L':'#2b2b2e','cheek_R':'#2b2b2e','bulkhead':'#2b2b2e','nose_cowl':'#2b2b2e',
       'lamp_housings':'#151515','lamp_lenses':'#ffe9a8','dash_pod_placeholder':'#2c7a4b','dash_bracket_alu':'#1a1a1a','top_cradle_forged':'#4a4a4c',
       'cheeseboard_alu':'#b9bfc6','tablet_tab_a9_placeholder':'#1a3d8f','visor_polycarb':'#5f6f7a','button_heads_ti':'#d8d8d8'}
doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
for k, c in COL.items():
    s = TopoDS_Shape(); BRepTools.Read_s(s, f'tw3/out3/{k}.brep', BRep_Builder())
    lab = st.AddShape(s, False); TDataStd_Name.Set_s(lab, TCollection_ExtendedString(k))
    r, g, b = mc.to_rgb(c); ct.SetColor(lab, Quantity_Color(r, g, b, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
w = STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True); w.Transfer(doc, STEPControl_AsIs)
print(w.Write('tw3/out3/nav-tower-v2.step'))
