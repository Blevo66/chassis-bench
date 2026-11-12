# Rocker H mock-up print set

Rocker H on the XL lower mount, dogbone to the CRF lug, XR250R shock 380/95, stock spring. About 215 mm wheel travel, 9% rising rate.

| File | Print | Notes |
|---|---|---|
| rocker-h-16mm.stl | 1 | 16 mm plate, holes 10.8 (M10). About 247 x 179 mm, lies flat |
| dogbone-134-12mm.stl | 1 | 134.1 centres. Rocker end 10.8, lug end 12.8 (M12) |
| dogbone-130 / 138 | optional | Test lengths |
| spacer-pivot-12mm-x2.stl | 2 | Centres the 16 mm rocker in the 40 mm XL lower mount |
| spacer-lug-right-10.5mm.stl | 1 | Right side of the lug gap |
| spacer-lug-left-18.5mm.stl | 1 | Left side of the lug gap. The dogbone sits against the rocker's right face, about 4 mm right of the lug centre |

Mock-up only: fine to sit the bike on its wheels, not to ride or sit on.

## 30 mm version (2026-11-06)
- rocker-h-30mm-slotted.stl: 30 mm wide with an 11 mm slot at the dogbone eye (dogbone goes in the slot, double shear). Fits the XR clevis with ~2 mm each side.
- spacer-pivot-5mm-x2.stl: print 2, centres the 30 mm rocker in the 40 mm XL mount.
- dogbone-134-10mm.stl (and 130/138): 10 mm thick to fit the 11 mm slot.

## CAD lug update (2026-11-06)
Joel confirmed the CRF250 arm CAD lug is right (209 along / 56 below the pivot-axle line). Same rocker H, but the dogbone is now 132 mm: 219 mm travel, 15% rising rate, ratio 2.47 -> 2.15.
- dogbone-132-10mm.stl (for the 30 mm slotted rocker) or dogbone-132-12mm.stl (16 mm rocker).
- With the 10 mm dogbone at the lug: spacer-lug-left-5.5mm.stl and spacer-lug-right-25.5mm.stl.

## Smooth version (2026-11-06)
- rocker-h-smooth-30mm-slotted.stl: same three hole positions as rocker H, curved outline with no clearance cutouts. Uses the same 132 dogbone (10 mm), 5 mm pivot spacers and 5.5 / 25.5 lug spacers.
- Drawing ../rocker-h-smooth-drawing.png, 1:1 DXF ../rocker-h-smooth.dxf.
- Model clearances through full travel: swingarm 5.5 mm at full droop opening to 18 mm at full bump, shock clevis body ~3 mm (clevis size is a guess, check it), frame scan 6 mm+.

## Strong version (2026-11-06, after stress check)
Flat 4 mm plates on the smooth shape reach ~1,400 MPa at full bump (too weak). Strong version: same holes, gusset filling the L, deeper under the shock clevis.
- rocker-h-strong-30mm-slotted.stl: solid print for test fitting.
- ../rocker-h-strong-plate.dxf: side plate, cut 2. 6 mm S355 (body ~180 MPa at full bump, ~360 at twice that) or 4 mm Strenx 700. 16 mm OD spacer tubes welded between plates at shock eye and pivot; 5 mm edge strip wrapped round top/bottom, stopping 25 mm short of the dogbone eye.
- ../rocker-h-strong-stress.png, ../rocker-h-strong-drawing.png, ../rocker-h-strong-3d-*.gif
- Clearance through travel: arm 4.7 mm at droop to 13 at bump, shock clevis ~4 (guessed clevis), frame scan 7+.

## Alloy version (2026-11-06)
- ../rocker-h-alloy.step and ../rocker-h-alloy.stl: 7075-T6 billet, 30 mm thick, same outline as the strong version, 8 mm rim, pocketed 11 mm deep both sides (8 mm centre web), full-thickness bosses, 11 mm dogbone slot. ~0.79 kg.
- Stress at full bump on the stock spring: ~185 MPa in the body (7075 yields ~500), ~370 at twice that load.
- Holes are drawn 10.8; for alloy, bore them for pressed-in steel bushes or needle bearings so bolts never run in the aluminium.
