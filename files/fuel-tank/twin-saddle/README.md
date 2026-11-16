# XL125R twin half-saddle tank, v8: bigger triangles (folds up to 200 mm)

Two half tanks, one either side of the spine, in the Kove-rally style: they drop down beside the engine, wide and low.
v8 (16 Nov). Joel asked for it simpler and picked "bigger triangles, about 200 mm". It is the v6 layout with about half the triangles:
- A flat deck on top of each half with room for a 100 mm filler cap, towards the back.
- The back tapers to an 80 mm vertical face for the seat.
- A short pointed front.

`v7-simple/` (big flat panels) is kept for comparison.

| | |
|---|---|
| Capacity | **6.1 L per half, 12.2 L total** (gross), so about 11.5 L usable. Stock XL125R tank is 8 L |
| Triangles | **46 per half**, longest fold line 168 mm (limit 200). Stations at X 20, 140, 260, 345, with 6 points round each section |
| Size | X 20 to 357, about 365 mm wide across the pods. Top 534 and pod bottoms 210 above the pivot |
| Filler pad | Flat deck on `strip-2`, 122 mm clear. The **100 mm circle is etched**, centre at X 201, 103 mm out from the spine centre, 505 up |
| Rear face | Flat and vertical, 78 mm tall, 69 mm wide per half, at X 20 |
| Steel | 1.2 mm DC01 / CR4, about 2.3 kg per half |
| Clearance to scan | 17 mm (right) and 23 mm (left) at the tightest point. The scan is about ±5 mm and its headstock end reads about 70 mm out, so check fork lock with the mock-up |
| Engine gap (GUESS) | The pods' lower inner walls are set for a ~200 mm wide cylinder head. **Measure the XL185 head and cam cover.** It's air-cooled, so leave the fins an air gap. The exhaust header must clear the right pod |

## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What | Real folds |
|---|---|---|
| `flat-rear-face.dxf` | Flat 78 mm vertical rear face | 0 |
| `flat-strip-1.dxf` | Rear strip (X 20 to 140), wraps right round | 9 |
| `flat-strip-2.dxf` | Middle strip (X 140 to 260), carries the filler pad | 9 |
| `flat-strip-3.dxf` | Front strip (X 260 to 345) | 10 |
| `flat-front-cone-top.dxf`, `flat-front-cone-bottom.dxf` | The short front point, in two pieces so each lies flat | 2 + 2 |
| `flat-baffle.dxf` | Baffle at mid length, holes plus a drain notch | 0 |

How it goes together:
- Every strip closes on itself at the **inner top edge** (against the spine, so the seam is hidden) and unfolds exactly flat. The strips butt-weld to each other, the rear face closes the back and the two point pieces close the front.
- **Fold lines are on layer `ETCH_FOLD`**: ask the laser shop to etch them, not cut. Each line is labelled with its angle and `out` or `IN`. Folds under 3° aren't drawn, so leave those flat.
- Fold one strip at a time over the printed mock-up as a buck, then tack strip to strip.

## Fittings (not drawn yet)
- **Fillers:** one per half on the flat deck (twin caps, 100 mm space each, etched on strip-2).
- **Tap:** the lowest point is the front bottom of each pod. Put the tap bung there on one half, and a crossover spigot low at the front of each pod's inner wall, with a hose between them under the head, so one tap drains both sides.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side with a welded cup and grommet. A laser-cut bridge strap joins the halves at the rear and bolts through a rubber to the XL's rear tank tab. Needs tape measurements (below).

## Mock-up (Bambu)
3 pieces per half: `mockup-left-rear.stl`, `mockup-left-front-upper.stl`, `mockup-left-front-lower.stl`, and the same three for the right. Each lies on its biggest flat face and fits the X1C bed (largest 247 x 204 x 174 mm). Print with 2 walls and 5 % infill, tape them together and sit them on the frame. They also make a buck to fold the steel strips over.

Check: fork tubes and front tyre at full lock both ways, the cylinder head, cam cover and fins between the pods, the exhaust header on the right, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, spacing side to side, and diameter.
2. Rear tank tab: distance forward of and above the pivot, and hole size.
3. Width of the XL185 cylinder head and cam cover, and the height of the top of the engine under the front of the tank.

## Rebuild
`NAR=6 python3 build8.py OUTDIR` then `python3 render8.py OUTDIR` (needs trimesh, ezdxf, shapely 2, matplotlib, rtree, mapbox_earcut, networkx).
- `tank.py` holds the base sections.
- `tri3.py` builds the stations, the flat deck and rear face, the staggered loft and the front point. It uses the helpers in `tri.py`.
- `XS`, `NAR`, `FTS`/`FTO` and `PADBAND` are environment variables: the stations, points per section, front-point size and offset, and which strip carries the filler.
- `v3-prism/` is the older straight-folded version.
