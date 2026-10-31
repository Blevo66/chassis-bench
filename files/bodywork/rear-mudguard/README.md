# Rear mudguard v1 (mock-up): retro modern, printed in 3 parts

A slim, modern-MX-style tail with a squared-off 80s Honda look: a flat crowned top, sharp 45° chamfered shoulders and straight side skirts. It's printed in 3 parts that are pinned and glued together.

## Downloads (raw links, work on the phone)

Print-ready (each stands on its front face, no supports needed):
- [Part 1, front (under the seat, carries the tab mounts)](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/print-part1-stand-on-end.stl): 53 x 146 x 199 mm
- [Part 2, middle](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/print-part2-stand-on-end.stl): 49 x 184 x 190 mm
- [Part 3, tail (with 2 plate-hanger holes)](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/print-part3-stand-on-end.stl): 33 x 184 x 190 mm

For Fusion (bike position, same coordinates as the frame scan, so insert at the origin): [whole guard](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/rear-mudguard-assembled.stl)

Pictures: [side view with frame scan and tyre](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/rear-mudguard-side.png), [3D view](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-aprb8e/files/bodywork/rear-mudguard/rear-mudguard-3d.png)

## Fitting

- **Side tabs:** M6 bolts through the skirts at 340 mm behind and ~325 mm above the swingarm pivot. The holes are **slotted ±5 mm up and down**, because the tab height came off the phone scan. The skirts are 146 mm across the outside, to sit inside the tabs, so pack with washers if there's a gap. Use big washers (penny washers) on the outside.
- **Front:** one M6 hole on top, under the rail cross-member (~253 mm behind the pivot). A rubber-lined P-clip round the cross tube bolts down into it, so the frame isn't modified. Add a spacer if needed.
- **Tail:** two M6 holes, 60 mm apart, 45 mm from the end, for a separate plate and light hanger (still to design).

## Joints (pinned and glued)

- The wall goes from 3 mm to 8 mm over the last ~12 mm at each joint, which gives a wide glue face and stiffens the joint.
- Each joint has 5 pin holes, 3.2 mm across and 12 mm deep each side (3 on top, 1 in each skirt). Use 3 mm steel dowels, or 2.85 mm filament offcuts.
- Glue: TPU takes flexible CA or a polyurethane glue. **PP barely glues.** For PP, plastic-weld the seam with a soldering iron and a PP rod, or swap the pins for M3 bolts.

## Print settings

- **Filament:** TPU 68D (easiest), or PP on a PP sheet or PP tape. PETG is fine for a fit-check mock-up.
- 4-5 walls; the shell is only 3 mm, so it prints as solid walls. Add a brim, since each part stands on a thin edge.
- Standing on end puts the layers across the guard's length. That's fine for TPU, which bonds very well between layers. For PP, keep the chamber warm.

## Clearance (checked through the whole travel)

- The tyre was modelled as 340 mm radius and 120 mm wide (18" 110/100 knobby), with the CRF250 arm at 580 mm, from full droop (24.2° down) to full bump (2.9° up), as on the bench XR tab.
- The top centre clears the tread by **25 mm at full bump**, tightest about 565 mm behind the pivot.
- The tightest point overall is **12.7 mm**, between the bottom inside edge of the skirt (just behind the rails) and the tyre shoulder at full bump.

## Rerun with real numbers

Edit the inputs at the top of `make_rear_mudguard.py` (tab position, `TAB_GAP`, tyre size, the `CTRL` top line), then run `python3 make_rear_mudguard.py` and `python3 preview.py <outdir> <frame scan STL>`. It needs numpy, trimesh and manifold3d.
