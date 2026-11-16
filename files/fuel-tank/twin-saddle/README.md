# XL125R twin half-saddle tank, v6: big triangles, flat filler deck, 80 mm seat face

Two half tanks, one either side of the spine, in the Kove-rally style: they drop down beside the engine, wide and low.
v6 (16 Nov), from Joel's notes and his marked-up picture:
- Big crisp triangles, every fold line 148 mm or shorter.
- A flat deck on top of each half, with room for a 100 mm filler cap towards the back.
- The back tapers down to an 80 mm vertical face for the seat to run up to.
- The pods stay full and rounded at the bottom front, closing to a short point (no flat front).

Laser-cut, folded by hand and MIG welded. Modelled against the frame scan (`files/frame-scan`: mm, origin = swingarm pivot, X forward, Y left, Z up).

| | |
|---|---|
| Capacity | **6.7 L per half, 13.5 L total** (gross), so about 12.5 L usable. Stock XL125R tank is 8 L |
| Size | X 20 to 357. About 365 mm wide across the pods. Top 535 and pod bottoms 186 above the pivot |
| Triangles | 88 per half, all fold lines 148 mm or shorter. The only edges over 150 are the flat deck's diagonal and the flat rear face, and neither is a fold. Stations at X 20, 80, 150, 265, 345 |
| Filler pad | Flat deck on `strip-3` (X 150 to 265), 120 mm clear circle, centre at X 208, 102 mm out from the spine centre, 507 up. A **100 mm circle is etched** on the DXF: cut the hole to suit your filler neck |
| Rear face | Flat, vertical, **80 mm tall** (69 mm wide per half) at X 20. The seat runs up to it |
| Steel | 1.2 mm mild steel (DC01 / CR4). About 2.4 kg per half, 4.9 kg for the pair before fittings |
| Clearance to scan | 20 mm (left) and 25 mm (right) at the tightest point. The scan is about ±5 mm and its headstock end reads about 70 mm out, so check fork lock with the mock-up |
| Engine gap (GUESS) | The pods' lower inner walls are set for a ~200 mm wide cylinder head. **Measure the XL185 head and cam cover.** It's air-cooled, so leave the fins an air gap. The exhaust header must clear the right pod |

## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What |
|---|---|
| `flat-rear-face.dxf` | Flat 80 mm vertical rear face |
| `flat-strip-1.dxf` to `flat-strip-4.dxf` | Strips that wrap right round the tank, rear to front. `strip-3` carries the filler pad |
| `flat-front-cone.dxf` | The short front point: a fan of triangles |
| `flat-baffle.dxf` | Baffle at mid length, 28 mm holes plus a drain notch. Tack it in before closing |

How it goes together:
- Every strip closes on itself at the **inner top edge** (against the spine, so the seam is hidden) and unfolds exactly flat. The strips butt-weld to each other round the tank, the rear face closes the back and the cone closes the front.
- **Fold lines are on layer `ETCH_FOLD`**: ask the laser shop to etch (mark) them, not cut. Each line is labelled with its angle and `out` or `IN`. Folds under 3° aren't drawn, so leave those flat. That leaves about 13 folds per strip.
- Fold one strip at a time over the printed mock-up as a buck, then tack strip to strip.

## Fittings (not drawn yet)
- **Fillers:** one per half on the flat deck (twin caps, 100 mm space each, etched on strip-3).
- **Tap:** the lowest point is the front bottom of each pod. Put the tap bung there on one half, and a crossover spigot low at the front of each pod's inner wall, with a hose between them under the head, so one tap drains both sides.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side with a welded cup and grommet. A laser-cut bridge strap joins the halves at the rear and bolts through a rubber to the XL's rear tank tab. Needs tape measurements (below).

## Mock-up (Bambu)
3 pieces per half: `mockup-left-rear.stl`, `mockup-left-front-upper.stl`, `mockup-left-front-lower.stl`, and the same three for the right. Each lies on its biggest flat face and fits the X1C bed (largest 248 x 225 x 174 mm). Print with 2 walls and 5 % infill, tape them together and sit them on the frame. They also make a buck to fold the steel strips over.

Check: fork tubes and front tyre at full lock both ways, the cylinder head, cam cover and fins between the pods, the exhaust header on the right, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, spacing side to side, and diameter.
2. Rear tank tab: distance forward of and above the pivot, and hole size.
3. Width of the XL185 cylinder head and cam cover, and the height of the top of the engine under the front of the tank.

## Rebuild
`python3 build6.py OUTDIR` then `python3 render6.py OUTDIR` (needs trimesh, ezdxf, shapely 2, matplotlib, rtree, mapbox_earcut, networkx).
- `tank.py` holds the base sections.
- `tri3.py` builds the stations, the flat deck and rear face, the staggered loft and the front point. It uses the helpers in `tri.py`.
- In `build6.py`, `XS` sets the stations, `FT` the size of the front point, and `NAR` the number of points round each section.
- `v3-prism/` is the older straight-folded version.
