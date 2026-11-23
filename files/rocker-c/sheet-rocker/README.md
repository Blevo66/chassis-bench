# Sheet-metal rocker mock-up (sit-and-bounce only)

Two identical plasma-cut plates, joggled, plus webs and two tubes, MIG'd together. Plain M10 bolts, no bushes.
Same P / S / D hole centres as rocker v7. Origin = pivot hole, X forward.

## Cut list (5 mm mild steel, recommended)
- 2x plate `sheet-rocker-5mm-flat.dxf` (identical, layer CUT). Plasma the 8 mm pilots (PILOT_8), drill to 10.5 (DRILL_10.5).
- 4x webs, 19.2 wide x 50 / 40 / 30 / 54 long (also on the DXF, same sheet).
- 2x tube 20 OD x 10 ID (5 wall), 19.2 long, drill out to 10.5. At P and S between the plates.

## Joggle
- Two 45 deg bends, opposite ways, on the BEND lines. Offset 17.25 mm (lower arm moves over to centre the dogbone slot on the old clevis centre).
- Inside radius ~5 mm. Developed length is already in the flat pattern (+6.6 mm past the jog).
- Both plates bend the SAME way: jog comes towards you looking at the drawing as printed.
- Bends are only ~24 mm apart, too close for most press brakes: easiest is heat + vice, or a joggle die at the cutters.

## Assembly widths (5 mm)
- Upper body: 29.2 outside, 19.2 between plates -> printed spacers to fill the 30 shock clevis and 40 frame mount.
- Lower cheeks: slot 19.2, centred on the old dogbone line -> printed spacers either side of the dogbone.
- Web 4 = the floor of the dogbone slot just past the jog. It stops the jog straightening under load. Check the dogbone clears it through the travel.

## Strength (hand calc, real 9.2 kg/mm spring)
| case | joggle, 5 mm, no web 4 | 5 mm with web 4 | 6 mm with web 4 |
|---|---|---|---|
| Sitting at sag (~0.4 of bump) | ~150 MPa | ~60 MPa | ~45 MPa |
| Full-bump slam | ~380 MPa (bends) | ~150 MPa | ~115 MPa |
Mild steel yield ~275 MPa. Bolt bearing and hole tear-out are fine at 5 mm.

Mass ~1.6 kg (5 mm), ~1.9 kg (6 mm). 6 mm files included: slot narrows to 17.2.
