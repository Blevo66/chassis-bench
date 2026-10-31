# Mock-up rocker: rocker B, 82 mm dogbone, XR250R shock

Printable side-profile rocker for bolting up as soon as the '86 XR250R shock (380 / 95, clevis bottom) arrives.
Layout: rocker on the frame's lower mount (22 behind / 29 below the pivot, 10 mm left line), dogbone back to the
CRF250 arm lug (200 along / 50 below), shock top 55 in front / 292 up. Rocker eyes 111 / 152.7 mm, 65° apart.
Same numbers as the bench's "XR250R rocker on frame" tab, button "Rocker B, 82 dogbone". 266 mm wheel travel, 19% rising rate.

## Downloads (raw links, work on the phone)

- **Whole plate for Bambu Studio** (rocker, dogbone, 2 pivot spacers, 2 lug packers): [rocker-B82-mockup-plate.3mf](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/rocker-B82-mockup-plate.3mf)
- Rocker only: [rocker-B82-mockup.stl](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/rocker-B82-mockup.stl) (141 x 168 x 16 mm)
- Dogbone only: [dogbone-82-mockup.stl](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/dogbone-82-mockup.stl) (82 mm centres, 12 mm thick)
- Pivot spacer (print 2): [pivot-spacer-12mm.stl](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/pivot-spacer-12mm.stl)
- Lug packer (print 2): [lug-packer-14.5mm.stl](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/lug-packer-14.5mm.stl)
- Pictures: [in the arm, droop / mid / bump](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/rocker-B82-mockup-preview.png), [rocker profile](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-4mdvbi/files/rocker-mockup/rocker-B82-mockup-profile.png)

Print flat as laid out, no supports. PETG or PLA, 4 walls, 25-40% infill. It's for bolting up and cycling by hand with the
spring off, not for riding.

## How the profile was cut

Starts as the hull of the three bosses, then removes everything the arm sweeps through relative to the rocker from full
droop (shock 380, arm 24.2° down) to full bump (shock 285, arm 2.9° up), plus 4 mm. The arm shape is Joel's CRF250 arm
model sliced every 2 mm across x = -12 to +27 mm (the rocker plate, the dogbone bar and the shock clevis zone), lined up
on the bench's lug at 200 / -50. In that band the arm is only the cross-member box and the lug: the legs are outboard and
there is no pivot tube in the middle, so the front of the rocker is free.

Checked through the whole travel:
- Rocker to arm (model slice): **4 mm at the tightest, at full droop**, where the shock arm of the rocker passes the front top corner of the cross-member. That's the first thing to look at when it's bolted up.
- The bench's own cross-member outline is a bit fatter at that corner (it's a silhouette across the full width) and shows touching there. If the real arm is fatter than the model in the middle, file that corner of the print.
- Dogbone bar to the arm: 16 mm.
- Rocker to the bottom of the shock: 2 mm, but against a **placeholder** clevis body (starts 20 mm up the shock from the bolt, 40 mm wide).
- The rocker's shock arm runs through a ~20 mm corridor between the cross-member and the shock body, so the neck is ~14 mm wide. Fine in plastic for a mock-up; in laser-cut steel it's fine too, but this is the spot that sets the real part.

## Assembly (left side view: pivot front-bottom, dogbone rear-bottom, shock eye up)

- Frame mount (40 mm): rocker plate 16 + a 12 mm spacer each side.
- Shock: the rocker's top end is a single 16 mm tongue into the XR clevis on the M10 bolt.
- Dogbone: one 12 mm bar, bolted beside the rocker's **right** face at the dogbone eye (single shear, mock-up only). That puts it on the lug's centre (~4.5 mm right of the arm centre), so it runs straight back into the lug clevis with a 14.5 mm packer each side (41 mm gap). The final part uses rod ends instead.

## Placeholders (measure, then I can re-run it)

| What | Used | Notes |
|---|---|---|
| Rocker plate / tongue thickness | 16 mm | Must fit the XR clevis gap. Sand it or tell me the gap. |
| Pivot bolt hole (frame mount) | 10.4 mm | XL lower bolt size not measured. Drill out to suit. |
| Rocker dogbone hole | 10.4 mm | Drill out to suit. |
| Shock bolt hole | 10.4 mm | M10 (measured). |
| Lug end of dogbone, packers | 12.4 mm | Arm model's lug hole is 12.8, so probably M12. Check. |
| Shock clevis body | 20 mm up from the bolt, 40 wide | Measure: bolt centre to underside of the clevis bridge, and the body width. |

## Files

- `design.py`: makes everything (`python3 design.py`; needs numpy, shapely, manifold3d, trimesh, matplotlib). Settings at the top.
- `geom.py`: the bench's linkage maths in Python (rocker B, 82 dogbone).
- `make_arm_section.py` / `arm_section_rocker_band.json`: the arm slice used for clearance.
- `rocker-B82-outline.json`: the profile as coordinates (pivot at 0,0, dogbone eye on +x), for Fusion or the laser cutter.
