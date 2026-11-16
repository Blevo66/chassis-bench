# XL125R twin half-saddle tank, v4: rounded low-poly side pods

Two half tanks, one either side of the spine, in the Kove-rally style: they drop down beside the engine, wide and low.
v4 (16 Nov, Joel: "use triangles with sides no longer than 150 mm to make it more rounded") rounds every corner of the v3 shape and covers it in flat triangles. Each triangle is a flat bit of sheet, and the folds between them give the rounded, faceted look.
Laser-cut, folded by hand and MIG welded. Everything was modelled against the frame scan (`files/frame-scan`: mm, origin = swingarm pivot, X forward, Y left, Z up).

| | |
|---|---|
| Capacity | **7.7 L per half, 15.4 L total** (gross), so about 14.5 L usable. Stock XL125R tank is 8 L. To get back to about 12 L, raise the pod bottoms to about 200 mm |
| Size | 325 mm long (X 20 to 345). About 410 mm wide across the pod bottoms at the front and about 240 mm at the knees. Pod bottoms are 120 mm above the pivot at the front, rising to 340 at the rear |
| Triangles | 108 per half, **longest side 138 mm** (limit 150). 18 points round each section, at 4 stations along the tank (X 20, 128, 237, 345) |
| Steel | 1.2 mm mild steel (DC01 / CR4). About 2.9 kg per half, 5.7 kg for the pair before fittings |
| Clearance to scan | 12 mm each side at the tightest point. The scan is about ±5 mm and its headstock end reads about 70 mm out, so check with the mock-up |
| Engine gap (GUESS) | 250 mm between the pods' lower inner walls, for the cylinder head. **Measure the XL185 head and cam cover.** It's air-cooled, so leave the fins an air gap. The exhaust header must clear the right pod |

## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What | Size flat |
|---|---|---|
| `flat-strip-1.dxf` | Ring strip round the tank, rear (X 20 to 128) | 369 x 255 mm |
| `flat-strip-2.dxf` | Ring strip, middle (X 128 to 237) | 617 x 301 mm |
| `flat-strip-3.dxf` | Ring strip, front (X 237 to 345) | 808 x 373 mm |
| `flat-front-cap.dxf` | Flat front end plate | 168 x 430 mm |
| `flat-rear-cap.dxf` | Flat rear end plate | 81 x 116 mm |
| `flat-baffle.dxf` | Baffle at mid length, 28 mm holes plus a drain notch at the bottom. Tack it in before closing | 120 x 268 mm |

How it goes together:
- Each ring strip wraps right round the tank and closes on itself at the **inner top edge** (against the spine, so the seam is hidden). Every point of a strip sits on its edge, so each one unfolds exactly flat. The three strips butt-weld to each other round the tank, and the caps weld onto the ends.
- **Fold lines are on layer `ETCH_FOLD`**: ask the laser shop to etch (mark) them, not cut. Each line is labelled with its angle and `out` (fold like the outside of a box) or `IN` (fold the other way). Folds under 3° aren't drawn: leave those flat, because the weld pulls them in. That leaves about 25 real folds per strip, all on lines 138 mm or shorter, so a vice and a folding bar or hand seamer will do them.
- Fold one strip at a time over the printed mock-up as a buck, then tack strip to strip.

## Fittings (not drawn yet)
- **Fillers:** one per half on the top (twin caps), or one filler plus a top vapour crossover.
- **Tap:** the lowest point is the front bottom of each pod. Put the tap bung there on one half, and a crossover spigot low at the front of each pod's inner wall, with a hose between them under the head, so one tap drains both sides.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side with a welded cup and grommet. A laser-cut bridge strap joins the halves at the rear and bolts through a rubber to the XL's rear tank tab. Needs tape measurements (below).

## Mock-up (Bambu)
3 pieces per half: `mockup-left-rear.stl`, `mockup-left-front-upper.stl`, `mockup-left-front-lower.stl`, and the same three for the right. Each lies on its biggest flat face and fits the X1C bed (largest 245 x 199 x 162 mm). Print with 2 walls and 5 % infill, tape them together and sit them on the frame. They also make a buck to fold the steel strips over.

Check: fork tubes and front tyre at full lock both ways, the cylinder head, cam cover and fins between the pods, the exhaust header on the right, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, spacing side to side, and diameter.
2. Rear tank tab: distance forward of and above the pivot, and hole size.
3. Width of the XL185 cylinder head and cam cover, and the height of the top of the engine under the front of the tank.

## Rebuild
`NST=4 NAR=18 python3 build4.py OUTDIR` then `python3 render4.py OUTDIR` (needs trimesh, ezdxf, shapely, matplotlib, rtree, mapbox_earcut, networkx).
- `tank.py` holds the base shape: the front and rear sections and their parameters.
- `tri.py` rounds the corners (`ring_poly`, radii 45/30 mm), spaces points closer together round the bends (`LAM`), and builds the triangle mesh and the strips.
- `NST` is the number of stations along the tank and `NAR` the number of points round each section. More of either gives smaller triangles and more folds.
- `v3-prism/` is the older straight-folded version.
