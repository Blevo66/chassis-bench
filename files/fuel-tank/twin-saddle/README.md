# XL125R twin half-saddle tank (fold-up steel), first pass

Two faceted half tanks, one either side of the spine, in the raw folded-sheet style. Laser-cut flat patterns, folded and MIG welded.
Everything was modelled against the frame scan (`files/frame-scan`, origin = swingarm pivot, X forward, Y left, Z up, mm).

| | |
|---|---|
| Capacity | **5.2 L per half, 10.4 L total** (gross). Usable is about 9.5-10 L. Stock XL125R tank is 8 L (Honda 1982 press release; moto-data.net says 9 L). |
| Size | 325 mm long (X 20 to 345), **320 mm wide at the front**, about 240 mm at the rear (knees) |
| Steel | **1.2 mm mild steel (DC01 / CR4)**. About 2 kg per half, 4 kg for the pair before fittings |
| Clearance to scan | 8 mm (left) and 14 mm (right) at the tightest point, where the spine splits into the seat rails. Scan is about ±5 mm, so check with the mock-up |

The side view is a straight-topped wedge for now. The plan is to match the stock XL125R tank's side silhouette, but deeper. That needs a square-on side photo of a stock XL125R to trace (see "Next").

## Parts (each DXF is the LEFT half: mirror it for the right, so make 2 of each)

| DXF | What | Folds |
|---|---|---|
| `flat-outer-skin.dxf` | Top, shoulder, outer side, lower chamfer | 3 folds (33°, 45°, 45°), all the same way |
| `flat-inner-pan.dxf` | Bottom, inner chamfer, inner wall (against the spine) | 2 folds (45°, 45°) |
| `flat-front-plate.dxf` | Front end cap (flat) | none |
| `flat-rear-plate.dxf` | Rear end cap (flat) | none |
| `flat-baffle.dxf` | Mid baffle, 3 x 32 mm holes, tack in before closing | none |

Layers: `CUT` (red), `BEND` (blue, fold lines, angle noted on layer `NOTE`). The fold angle is how far the sheet turns away from flat.

- The patterns are drawn to the outside surface with sharp folds. With folds of 45° or less in 1.2 mm, the error is well under 1 mm per fold, which a MIG seam takes up. If the laser shop also folds the parts (press brake), ask them to apply their own bend allowance.
- The two folded pieces meet along the top inner edge and the bottom outer edge, and those two seams are the long welds. The end plates sit inside the skins' ends: the skins are shortened by the sheet thickness so they butt onto the plate faces.
- All folds are open (no closed box), so a bench folder or a press brake can do them.

## Fittings (not drawn yet)
- **Fillers:** one per half on the top facet (twin caps, rally style), or one filler plus a top vapour crossover.
- **Tap:** weld-in bung at the rear-inner low point of one half. Fit a bottom crossover spigot on each half, joined by a hose under the spine, so one tap drains both sides.
- **Vent** on each cap or a breather spigot.
- **Mounts (bolt on only, nothing on the frame changes):** each half picks up the XL's own front tank peg on its side, with a welded cup and grommet on the inner wall. A laser-cut bridge strap joins the two halves at the rear and bolts through a rubber to the XL's rear tank tab. The scan isn't sharp enough to find the pegs, so these need tape measurements (see below).

## Mock-up (Bambu)
`mockup-left-front.stl`, `mockup-left-rear.stl` and the right-side pair are each half split at mid length, standing on the cut face. The largest is 245 x 123 x 162 mm. Print with 2 walls and 5 % infill. Tape the two pieces together and sit them on the frame.
Card is even quicker: print the DXFs at 100 % on paper, glue them to cereal-box card and fold.

Check with the mock-up: fork tubes at full lock both ways (the front corner is about 20 mm from the tube by my estimate), the cylinder head and cam cover under the front, the carb under the rear, the seat nose, and your knees standing up.

## To measure on the frame
1. Front tank pegs: distance forward of and above the swingarm pivot centre, peg spacing side to side, and peg diameter.
2. Rear tank tab: distance forward of and above the pivot, and the hole size.
3. Height of the top of the engine (cam cover) under the front of the tank, if the engine is in.

## Rebuild
`python3 build.py OUTDIR` then `python3 render.py OUTDIR` (needs trimesh, ezdxf, shapely, matplotlib, rtree). Shape parameters are at the top of `tank.py`. The front and rear sections keep parallel edges, so every face stays flat and the patterns still unfold.
