# XL125R twin half-saddle tank, v5: big crisp triangles, pointed ends

Two half tanks, one either side of the spine, in the Kove-rally style: they drop down beside the engine, wide and low.
v5 (16 Nov). Joel wanted fewer, bigger, crisp triangles (sides up to 150 mm) and no flat front or rear, so the ends taper to a point in triangles too.
Laser-cut, folded by hand and MIG welded. Everything was modelled against the frame scan (`files/frame-scan`: mm, origin = swingarm pivot, X forward, Y left, Z up).

| | |
|---|---|
| Capacity | **6.2 L per half, 12.4 L total** (gross), so about 11.5 L usable. Stock XL125R tank is 8 L |
| Size | X 0 to 365 (the front point sits 20 mm ahead of v3/v4, so check fork lock). About 365 mm wide across the pods, top 533 and pod bottoms 168 above the pivot |
| Triangles | **90 per half, longest side 149 mm** (limit 150). Rows are staggered half a step, so the triangles are near-equilateral: 9 points round each section at 5 stations (X 20, 80, 182, 285, 345), plus a point at each end |
| Steel | 1.2 mm mild steel (DC01 / CR4). About 2.3 kg per half, 4.6 kg for the pair before fittings |
| Clearance to scan | 13 mm (right) and 18 mm (left) at the tightest point. The scan is about ±5 mm and its headstock end reads about 70 mm out, so check with the mock-up |
| Engine gap (GUESS) | The pods' lower inner walls are set for a ~200 mm wide cylinder head. **Measure the XL185 head and cam cover.** It's air-cooled, so leave the fins an air gap. The exhaust header must clear the right pod |

## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What |
|---|---|
| `flat-rear-cone.dxf` | The pointed rear end: a fan of 9 triangles |
| `flat-strip-1.dxf` to `flat-strip-4.dxf` | Ring strips that wrap right round the tank, rear to front, 18 triangles each |
| `flat-front-cone.dxf` | The pointed front end: a fan of 9 triangles |
| `flat-baffle.dxf` | Baffle at mid length, 28 mm holes plus a drain notch. Tack it in before closing |

How it goes together:
- Every panel closes on itself at the **inner top edge** (against the spine, so the seam is hidden). Every point of a panel sits on its edge, so each one unfolds exactly flat. The strips butt-weld to each other round the tank, and the two cones close the ends.
- **Fold lines are on layer `ETCH_FOLD`**: ask the laser shop to etch (mark) them, not cut. Each line is labelled with its angle and `out` or `IN` (which way to fold). Folds under 3° aren't drawn: leave those flat. That leaves about 15 folds per strip.
- Fold one strip at a time over the printed mock-up as a buck, then tack strip to strip.

## Fittings (not drawn yet)
- **Fillers:** one per half on the top (twin caps), or one filler plus a top vapour crossover.
- **Tap:** the lowest point is the front bottom of each pod. Put the tap bung there on one half, and a crossover spigot low at the front of each pod's inner wall, with a hose between them under the head, so one tap drains both sides.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side with a welded cup and grommet. A laser-cut bridge strap joins the halves at the rear and bolts through a rubber to the XL's rear tank tab. Needs tape measurements (below).

## Mock-up (Bambu)
3 pieces per half: `mockup-left-rear.stl`, `mockup-left-front-upper.stl`, `mockup-left-front-lower.stl`, and the same three for the right. Each lies on its biggest flat face and fits the X1C bed (largest 245 x 200 x 182 mm). Print with 2 walls and 5 % infill, tape them together and sit them on the frame. They also make a buck to fold the steel strips over.

Check: fork tubes and front tyre at full lock both ways, the cylinder head, cam cover and fins between the pods, the exhaust header on the right, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, spacing side to side, and diameter.
2. Rear tank tab: distance forward of and above the pivot, and hole size.
3. Width of the XL185 cylinder head and cam cover, and the height of the top of the engine under the front of the tank.

## Rebuild
`NAR=9 TIP=60 TS=0.5 AO=20 python3 build5.py OUTDIR` then `python3 render5.py OUTDIR` (needs trimesh, ezdxf, shapely, matplotlib, rtree, mapbox_earcut, networkx).
- `tank.py` holds the base shape: the front and rear sections and their parameters.
- `tri2.py` lays out the stations, staggered rings and pointed ends. It uses the helpers in `tri.py`.
- `NAR` is the number of points round each section (fewer gives bigger triangles). `TIP` is the length of each tapered end, `TS` the size of the tip ring, and `AO` how far the point sticks out.
- `v3-prism/` is the older straight-folded version.
