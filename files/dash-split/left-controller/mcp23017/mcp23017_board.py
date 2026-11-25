"""Waveshare MCP23017 IO Expansion Board, from Waveshare's dimension picture (2026-11-25).
Origin: board bottom-left corner (the end with the 2 mounting holes), BOTTOM face of the PCB at Z=0.
X along the 38 mm length (towards the white PH2.0 plug), Y along 23 mm, Z up through the components.
From the drawing: 38 x 23, R1 corners, header rows 20.32 apart, 2.54 pitch, first pin 5.96 from left edge,
mounting holes 19.00 apart. GUESSES: PCB 1.6 thick, hole dia 2.0 at 2 mm from the edges, plug size
(standard 6-pin PH2.0 side-entry), chip/parts heights, header pin lengths.
Headers are a SEPARATE body: hide it if you'll solder wires straight to the holes (they're not needed).
"""
import cadquery as cq

L, Wd, T = 38.0, 23.0, 1.6
pcb = (cq.Workplane("XY").rect(L, Wd, centered=False).extrude(T).edges("|Z").fillet(1.0))
holes = [(2.0, 2.0), (2.0, Wd - 2.0)]
pcb = pcb.faces(">Z").workplane(origin=(0, 0, T)).pushPoints(holes).hole(2.0)
# 2 x 10 header holes + 6-pin I2C column at the left end
row_y = [(Wd - 20.32) / 2, (Wd + 20.32) / 2]
pins = [(5.96 + i * 2.54, y) for y in row_y for i in range(10)]
col = [(2.0 + 0.0, Wd / 2 + (k - 2.5) * 2.54) for k in range(6)]
pcb = pcb.faces(">Z").workplane(origin=(0, 0, T)).pushPoints(pins + col).hole(1.0)

chip = cq.Workplane("XY").box(10.2, 5.3, 1.8, centered=(True, True, False)).translate((17.4, Wd / 2, T))
# PH2.0 6-pin side-entry housing, opening facing +X at the right end
plug = cq.Workplane("XY").box(6.0, 14.9, 4.5, centered=(False, True, False)).translate((L - 6.0, Wd / 2, T))
plug = plug.faces(">X").workplane().rect(12.4, 3.0).cutBlind(-4.0)

hdr = None
for y in row_y:
    strip = cq.Workplane("XY").box(10 * 2.54, 2.5, 2.5, centered=(False, True, False)).translate((5.96 - 1.27, y, T))
    for i in range(10):
        p = cq.Workplane("XY").box(0.64, 0.64, 11.5, centered=(True, True, False)).translate((5.96 + i * 2.54, y, T - 3.0))
        strip = strip.union(p)
    hdr = strip if hdr is None else hdr.union(strip)

a = cq.Assembly(name="waveshare_mcp23017")
a.add(pcb, name="pcb", color=cq.Color(0.1, 0.25, 0.6))
a.add(chip, name="mcp23017_chip", color=cq.Color(0.1, 0.1, 0.1))
a.add(plug, name="ph2_plug", color=cq.Color(0.95, 0.95, 0.9))
a.add(hdr, name="headers_optional", color=cq.Color(0.85, 0.7, 0.2))
a.save("waveshare-mcp23017-board.step")
cq.exporters.export(pcb.union(chip).union(plug).union(hdr), "waveshare-mcp23017-board.stl")
print("ok")
