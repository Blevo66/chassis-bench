# XL125R frame scan, ready for Fusion 360

Made from `scan1-2026-10-11.stl` (Scaniverse, iPhone).

## The files

| File | What it is | Use it for |
|---|---|---|
| `xl125r-frame-scan-light.stl` (or `.obj`) | 9,200 triangles, closed (watertight) | Convert to a solid body in Fusion |
| `xl125r-frame-scan-full.stl` | ~37,000 triangles, closed | Reference mesh to look at and section |
| `xl125r-frame-datums.step` | Solid pivot bolt, pivot faces, both mount pins | Accurate points to design against |
| `preview.png` | Picture of the result | Quick check |
| `make_fusion_scan.py` | The script that made the meshes | Rerun it on a better scan |

## Coordinates (all files share them)

- Units: **mm**
- Origin: **swingarm pivot centre**, on the frame centreline
- **X forward**, **Y left**, **Z up**. So the pivot axis is the Y axis and the bike's centre plane is XZ.
- Turned about the pivot so the top shock mount sits where your tape put it: **55 mm ahead, 292 mm up**. The lower dogbone mount is at 22 mm behind, 29 mm below. Both mounts are 10 mm left (Y = +10).

## What was done to the scan

1. Metres to mm.
2. Cut away the plank it sat on (it was melted into the bottom of the frame).
3. Moved the pivot to the origin and set the axes as above.
4. Scaled ×0.969 (the scan read about 3% big) and rotated 12.4° about the pivot (the frame sat nose-down on the stand). These are the same numbers as the earlier linkage comparison.
5. Closed the holes so it's watertight.
6. Light version: lightly smoothed and cut down to 9,200 triangles.

## In Fusion 360

1. **Insert > Insert Mesh**, pick the light STL, set units to **millimetres**. If it comes in lying on its back, your Fusion is set to "Y up": rotate it −90° about X in the insert dialog (or set Preferences > General > Default modelling orientation to Z up before starting the design).
2. Don't move it. The origin is already the pivot.
3. To get a solid: right-click the mesh body > **Convert Mesh** (Mesh tab > Modify > Convert Mesh), method **Faceted**. It's a closed mesh under 10,000 triangles, so this should work. Use it to check clearances and for Combine/cut tests.
4. Insert `xl125r-frame-datums.step` (**Insert > Insert Derive** or just open it and copy in). Its parts sit at the right positions already.
5. Design against the datum parts and your tape numbers. Use the mesh for shape and clearance only.

## How accurate is it?

- It's a phone scan: tubes are lumpy and blobby, roughly ±5 mm, more around gussets.
- Only two points are pinned to tape: the pivot and the top shock mount. The 12.4° turn comes from them, so anything far from that line (steering head, rear loop) could be out by more.
- "Level" here means "matches your 55/292 tape". It's not ride height. If you want the bike at ride height, rotate everything about the Y axis (the pivot).
- Left/right: the scan's handedness wasn't checked against a real feature. If the 10 mm-left shock mount looks wrong against the mesh, mirror the mesh about the XZ plane.
- Pin diameters in the STEP (10 mm) are placeholders. Measure them.
