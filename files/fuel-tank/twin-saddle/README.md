# XL125R twin half-saddle tank (fold-up steel), v3: Kove-rally style side pods, wider and lower

Two faceted half tanks, one either side of the spine, in the raw folded-sheet style. v2 (16 Nov) dropped each half down the side of the engine like a Kove rally tank. v3 (Joel: "wider and lower") takes the pods down to 120 mm above the swingarm pivot at the front and 410 mm wide. The top stays narrow at the knees, the lower part steps out to clear the cylinder head, and the bottom line rises towards the seat. Laser-cut flat patterns, folded and MIG welded.
Everything was modelled against the frame scan (`files/frame-scan`, origin = swingarm pivot, X forward, Y left, Z up, mm).

| | |
|---|---|
| Capacity | **8.0 L per half, 16 L total** (gross). Usable is about 15 L. Stock XL125R tank is 8 L (Honda 1982 press release). To get back to about 12 L, raise the pod bottoms to about 200 mm or trim the top |
| Size | 325 mm long (X 20 to 345). **410 mm wide across the pod bottoms at the front**, about 240 mm at the rear (knees). Pod bottoms 120 mm above the pivot at the front, 440 mm below the tank top, rising to 340 at the rear |
| Engine gap (GUESS) | Lower inner walls are 125 mm each side of the spine centre (250 mm between the pods) for the cylinder head. That assumes the XL185 head is about 200 mm wide: **measure it**. It's air-cooled, so leave the fins an air gap and keep the pod fronts open to the wind. The exhaust header (right side) must clear the right pod |
| Steel | **1.2 mm mild steel (DC01 / CR4)**. About 3 kg per half, 6 kg for the pair before fittings. Full, the tank holds about 12 kg of fuel, carried low |
| Clearance to scan | 12 mm (left) and 10 mm (right) at the tightest point. Scan is about ±5 mm, and its front end (headstock) reads about 70 mm out, so check with the mock-up |


## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What | Folds |
|---|---|---|
| `flat-outer-skin.dxf` | Top, shoulder, outer side, lower chamfer | 3 folds (33°, 45°, 45°), all the same way |
| `flat-inner-pan.dxf` | Bottom, lower inner wall (engine side), 45° step over the head, upper inner wall (against the spine) | 3 folds: 92°, 45° **folded the opposite way** (the step), 45°. Each fold is labelled in the DXF |
| `flat-front-plate.dxf` | Front end cap (flat) | none |
| `flat-rear-plate.dxf` | Rear end cap (flat) | none |
| `flat-baffle.dxf` | Mid baffle, 28 mm holes and drain notches at the bottom. Tack it in before closing | none |

Layers: `CUT` (red), `BEND` (blue, fold lines, angle noted on layer `NOTE`). The fold angle is how far the sheet turns away from flat.

- The patterns are drawn to the outside surface with sharp folds. With folds of 45° or less in 1.2 mm, the error is well under 1 mm per fold, which a MIG seam takes up. If the laser shop also folds the parts (press brake), ask them to apply their own bend allowance.
- The two folded pieces meet along the top inner edge and the bottom outer edge, and those two seams are the long welds. The end plates sit inside the skins' ends: the skins are shortened by the sheet thickness so they butt onto the plate faces.
- All folds are open (no closed box), so a bench folder or a press brake can do them. The inner pan's step fold goes the other way from the rest.

## Fittings (not drawn yet)
- **Fillers:** one per half on the top facet (twin caps, rally style), or one filler plus a top vapour crossover.
- **Tap:** the lowest point is now the **front bottom of each pod**. Put the tap bung there on one half, and a crossover spigot on each pod's lower inner wall at the front, joined by a hose under the head, so one tap drains both sides. Or fit a tap on each side and Y them together.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side, with a welded cup and grommet on the inner wall. A laser-cut bridge strap joins the two halves at the rear and bolts through a rubber to the XL's rear tank tab. The scan isn't sharp enough to find the pegs, so these need tape measurements (see below).

## Mock-up (Bambu)
Each half is in 3 pieces: `mockup-left-rear.stl`, `mockup-left-front-upper.stl`, `mockup-left-front-lower.stl`, and the same three for the right. Each piece lies on its biggest flat face and fits the X1C bed (largest 249 x 218 x 162 mm). Print with 2 walls and 5 % infill. Tape the pieces together and sit them on the frame.
Card is even quicker: print the DXFs at 100 % on paper, glue them to cereal-box card and fold.

Check with the mock-up: fork tubes and front tyre at full lock both ways (the front corner is about 20 mm from the tube by my estimate), the cylinder head, cam cover and fins between the pods, the exhaust header on the right, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, peg spacing side to side, and peg diameter.
2. Rear tank tab: distance forward of and above the pivot, and the hole size.
3. Width of the XL185 cylinder head and cam cover, and the height of the top of the engine under the front of the tank. These set the gap between the pods.

## Rebuild
`python3 build.py OUTDIR` then `python3 render.py OUTDIR` (needs trimesh, ezdxf, shapely, matplotlib, rtree). Shape parameters are at the top of `tank.py`. The front and rear sections keep parallel edges, so every face stays flat and the patterns still unfold.
