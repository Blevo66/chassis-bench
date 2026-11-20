# XL125R frame: clean model from the scan (2026-11-20)

Built from Joel's `Frame Scan.stl` (Fusion export). Units: mm.

## Files
- `xl125r-frame-clean.step`: assembly with 3 parts: `frame` (solid), `fork_tube_L` / `fork_tube_R` (43 mm reference cylinders, bottom of bottom yoke to top of top yoke), and `steering_axis_ref` (a 2 mm rod on the steering axis).
- `xl125r-frame-clean.stl`: the frame only. `xl125r-frame-with-forks.stl`: the frame plus the fork tubes.
- `frame-scan-watertight-bike-aligned.stl`: the watertight scan, moved into the same coordinates so it overlays the model.
- `transform.json`: the 4x4 matrix that takes scan coordinates to model coordinates.
- `build2.py`: the build script (it needs the fitting data files in the working folder).

## Coordinates (model / bike frame)
- Origin: on the steering axis, at the bottom end of the head tube.
- X: lateral (+X = right side of the bike). The frame centreplane is X=0, set from the two fork axes.
- Y: rearward (-Y = forward, the same convention as the scan).
- Z: the scan's up direction with roll removed. **Whether this is truly vertical for the bike on its wheels is unknown.** The scan's own up direction was used.
- The scan was rolled about 2.6 deg and yawed about 3.8 deg relative to the bike. This frame removes both.
- Steering axis: rake 25.4 deg to Z, in the X=0 plane.

## Where each dimension comes from
| Feature | Value | Source / confidence |
|---|---|---|
| Steering axis | from both fork-tube axes (rms fit 0.9 to 1.3 mm), parallel to within 0.3 deg | scan, good |
| Fork c-c | 182.0 mm, both tubes 93.6 mm from the head axis (about 22 mm yoke offset) | scan, good |
| Fork tube OD | 43.0 | **Joel**. The scan reads only 30-34 because chrome scans thin. |
| Head tube OD | 50.0 | **Joel's clamp fit (R25 saddle)**. The scan reads about 53. |
| Head tube length | 161 (bottom just above the bottom yoke, top where the stem shows) | scan, about ±3 |
| Head bore | Ø47 x 15 bearing seats each end, Ø40 between | 47 from the bearing; **40 is a guess** |
| Backbone | oval, about 45 wide x 50 tall (clean section), growing toward the rear junction | scan section areas |
| Downtube | Ø31.4 (clean section), flares at the engine mount | scan |
| Brace | oval, 21 wide x 31 tall | scan |
| Rear tubes (to the scan's cut) | about 17x20 (right) and 19x24 (left), shapes as scanned | scan, rough; the cut ends are rough |
| Head gusset, rear junction | ruled loft through the scan's own cross-sections every 4 mm | scan, follows its bumps |
| Tank bosses | Ø27, tips at X -40.1 / +40.8, Y about 100, Z about 23 | scan. Their symmetry about X=0 (0.4 mm) is a good check on the centreplane. |

## Accuracy check
Model surface vs the scan: 93% of it is within 2 mm outside the scan, and 97% within 4 mm.
The biggest misses are the end caps at the scan cut and the downtube's engine-mount flare.
**Possible scale bias:** painted tubes may read about 1.5 mm oversize per side (the head tube reads 53 vs 50 real).
That would make the downtube and backbone sizes slightly large. Check them with calipers before you trust a tight fit.
