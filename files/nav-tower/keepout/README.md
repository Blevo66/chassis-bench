# Keep-out models for the headstock clamp (2026-11-19)

These are in the **same coordinates as Joel's Headstock clamp STEP** (mm). Import them into the clamp design at the origin with no move or rotation.
- Y runs along the head tube, starting from the clamp's bottom end.
- X is sideways.
- Z: negative is forward (away from the head tube). The head-tube centre line is X=0, Z=0.

| File | What it is |
|---|---|
| keepout-fork-sweep-40deg-clamp-coords.stl | All the space the forks, yokes and bars pass through between full left and full right lock (±40°). Keep about 8 mm away from it. |
| keepout-frame-clamp-coords.stl | Frame near the head (head tube, head box, tank bosses). |

Caveats (from the scan, roughly ±3 mm):
- Above clamp Y≈98 the scan wrongly marks the top of the head tube as part of the steering. So the sweep there is too fat, and the bar-clamp nuts are not clearly captured. Check that area on the bike.
- The tank is not in the scan.
- The current clamp v2 sits about 2 mm from the bottom-yoke sweep at its lower end (Y=0).
