# Rally nav tower, v0 layout (2026-11-17)

This is a layout block, not a styled part yet. It proves there is a clamp-on route from the frame to a tower that clears the forks, yokes and bars at full lock. Shapes are simple faceted hulls so you can restyle them for carbon moulds.

![views](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/tower-v0-views.png)

## Files (scan coordinates, mm, same frame as FRAME_FRONT_ALIGNED.step)
- [Whole assembly STL](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/nav-tower-v0-assembly-scan-coords.stl). Import it into Fusion on top of your scan and it should line up.
- Parts: [tower_shell](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/tower_shell.stl), [neck](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/neck.stl), [bridge](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/bridge.stl), [plate_L](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/plate_L.stl), [plate_R](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/plate_R.stl), [bolt1](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/bolt1.stl), [bolt2](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/bolt2.stl), [headlight](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/headlight.stl), [tablet_5in](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/tablet_5in.stl), [dash_3in_tft](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/dash_3in_tft.stl).
- [Steering sweep slices](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/steering-sweep-slices.png) and [frame side map](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-a69swg/files/nav-tower/frame-side-map.png).

Scan axes after the STEP's own placement transform: X lateral, **-Y forward**, Z up. Steering axis passes (2.6, -16.2, -9.4) with direction (0, 0.4705, 0.8824).

## How it holds on (no frame changes)
1. **Two side plates** (3 mm steel or alloy, laser-cut) lie on the head gusset sides. Each has a hole that slips over a 10 mm tank boss. The plates' front ends sit beside the head tube between the yokes.
2. **Two through-bolts** (M8 with spacer tubes) pass through the open triangle in the frame behind the head and pull the plates together, with TPU pads against the frame.
3. A **U-bridge** wraps the front of the head tube between the yokes and joins the plates. It bears on the head tube through a pad.
4. A **neck**, 34 mm wide, runs straight forward from the bridge through the gap between the fork tubes. That gap stays open at full lock. The tower bolts to the front of the neck.
5. The **tower shell** (carbon) carries the 5" headlight in its front face, the 3" TFT dash on its rear face, and the 5" tablet on a top deck tilted toward you.

## Clearances in the model (45° lock)
| Part | To steering sweep | Notes |
|---|---|---|
| Tower shell | 9 mm | tightest point is the rear-top corners vs the bars |
| Neck | 11.5 mm | between the fork tubes at full lock |
| Bridge | 5.7 mm | vs the yokes above and below |
| Plates | 7.8 mm | |
| Dash / tablet | 33 / 54 mm | |
The plates touch the frame by design at the tank bosses (that's the boss passing through the plate).

## Facts vs guesses
**From the scan (±3 mm or so):** fork tubes 182 mm c-c at 28° to scan Z; head tube ~54 OD; tank bosses at about (±40, 112, 53) scan, sticking out to ~40 mm from centre; open frame triangle behind the head.
**From Joel:** bosses are 10 mm with rubber bungs, and the tank slides over them; clamp only; carbon from printed moulds; 3" TFT dash, generic 5" tablet, ~5" round headlight; CR yoke offset 20 mm.
**Guesses (please check):**
- Steering lock 45° each way. If yours is more, the neck gap shrinks.
- Headlight 140 mm rim, 75 deep. Tablet in case 145x80x14. Dash module 80x58x14.
- Scan Z taken as vertical.
- Plate over the boss leaves only ~8 mm of boss for the tank's rubber bung.
- Cables, brake hose and wiring aren't in the scan. They'll need routing around the neck.
- No stress check yet. The neck is the critical section; I'd make it steel or alloy rather than carbon.
