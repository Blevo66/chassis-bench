"""RUNCCI-style 12 mm waterproof momentary push button (Amazon listing drawing, 2026-11-25).
Origin: centre of the button on the BACK face of the cap (= front face of the panel it mounts in).
+Z points out of the panel towards the rider. Units mm.
From the drawing: 18 overall (dome front to body end), dome 2.6, cap 5.5 long x 17.5 dia,
thread 11.8 dia (12 mm panel hole), solder tabs 3.6 long x 2.8 wide x 0.7 thick, slot 1.5.
Everything else (nut size, seal ring, body steps, tab spacing) is scaled off the picture: GUESSES.
"""
import cadquery as cq

CAP_D, CAP_L, DOME_H, DOME_D = 17.5, 5.5, 2.6, 14.0
THREAD_D, BODY_END = 11.8, -(18.0 - CAP_L - DOME_H)          # 18 overall -> body ends 9.9 behind panel
NUT_AF, NUT_T, NUT_Z = 16.0, 2.4, -2.0                       # guess
TAB_L, TAB_W, TAB_T, TAB_GAP = 3.6, 2.8, 0.7, 5.3            # tab spacing guessed from picture

cap = cq.Workplane("XY").circle(CAP_D / 2).extrude(CAP_L).edges(">Z").fillet(0.8)
# dome: spherical cap of height DOME_H on a DOME_D base
R = (DOME_D ** 2 / 4 + DOME_H ** 2) / (2 * DOME_H)
sphere = cq.Workplane("XY").sphere(R).translate((0, 0, CAP_L + DOME_H - R))
dome = sphere.intersect(cq.Workplane("XY").workplane(offset=CAP_L - 0.01).circle(DOME_D / 2).extrude(DOME_H + 0.02))
seal = cq.Workplane("XY").workplane(offset=-1.2).circle(13.0 / 2).circle(THREAD_D / 2).extrude(1.2)
thread = cq.Workplane("XY").workplane(offset=-5.0).circle(THREAD_D / 2).extrude(5.0)
nut = (cq.Workplane("XY").workplane(offset=NUT_Z - NUT_T).polygon(6, NUT_AF / 0.8660254).extrude(NUT_T)
       .faces(">Z").workplane().hole(THREAD_D + 0.2).edges("|Z").fillet(0.3))
body = cq.Workplane("XY").workplane(offset=-8.6).circle(11.0 / 2).extrude(3.6)
plinth = cq.Workplane("XY").workplane(offset=BODY_END).circle(9.0 / 2).extrude(1.3)
tabs = None
for y in (-TAB_GAP / 2, TAB_GAP / 2):
    t = (cq.Workplane("XY").box(TAB_W, TAB_T, TAB_L).translate((0, y, BODY_END - TAB_L / 2))
         .faces(">Y").workplane().center(0, -0.6).slot2D(2.0, 1.5, 90).cutThruAll())
    tabs = t if tabs is None else tabs.union(t)

button = cap.union(dome).union(seal).union(thread).union(body).union(plinth).union(tabs)
assy = cq.Assembly(name="button_12mm")
assy.add(button, name="button", color=cq.Color(0.15, 0.15, 0.15))
assy.add(nut, name="nut", color=cq.Color(0.75, 0.75, 0.78))
assy.save("button-12mm-runcci.step")
cq.exporters.export(button.union(nut), "button-12mm-runcci.stl")
# panel cutout helper: 12.2 mm hole (12 + 0.2 clearance for printing)
print("ok", button.val().BoundingBox().zmin, button.val().BoundingBox().zmax)
