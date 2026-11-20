# Nav tower v1 (3D): Dakar-style carbon skeleton

This is the first real 3D tower, built on the clean frame model (branch `claude/project-thread-lbn0s4`, `files/frame-scan/clean-model/`).
It uses the **same coordinates** as that model, so you can import it straight into Fusion on top of `xl125r-frame-clean.step`:
- Origin: on the steering axis, at the bottom of the head tube.
- X: to the right of the bike.
- -Y: forward.
- Z: up.
- Units: mm.

## Files
- `nav-tower-v1.step`: all parts as named, coloured solids.
- `nav-tower-v1-all.stl`: every part in one STL. `parts/*.stl` has each part on its own.
- `tower-v1-renders.png`, `tower-v1-hero.png`: renders with the frame, yokes, fork tubes and bars.
- `clearance.json`: the closest approach of each part to the steering sweep (forks, yokes and bars at ±40° lock, 2° steps) and to the frame.
- `src/`: the build scripts (Python, using OpenCascade).

## Parts
| Part | What it is |
|---|---|
| `neck_carbon` | Feet that bolt to the 4 M8 bosses (2 per side, 8.5 mm holes). The feet join a cross-bar in front of the head tube, and a ±22 mm wide spine runs forward between the yokes. The arms sit at X ±37.5 to 43.5 (the boss faces). |
| `cheek_L/R` | 4 mm carbon side cheeks at X ±99 to 103, with lightening windows. |
| `bulkhead`, `pod_front`, `chin` | The lamp pod: a sloped bulkhead kept clear of the sweep, an angled front plate with lamp holes, and a beak chin. |
| `lamp_housings`, `lamp_lenses` | A placeholder pair of 90 mm round lamps, 60 mm deep, at X ±52. |
| `dash_pod_placeholder`, `dash_bracket_alu` | The 133 x 99 x 53 dash on a folded alu bracket, leaning back 35°. |
| `top_cradle_forged` | The forged-carbon cradle, with 4 x M6 inserts on a 100 x 100 (VESA) square. |
| `cheeseboard_alu` | A 240 x 160 x 4 alu plate, with 6.5 mm holes on a 20 mm grid. |
| `tablet_tab_a9_placeholder` | The Tab A9, 211 x 125 x 8, on 12 mm standoffs. |
| `visor_polycarb` | A small smoked visor off the front edge of the cradle. |
| `button_heads_ti` | Bolt heads, for looks. |

## Closest approach (clearance.json)
| Part | To the 40° lock sweep | To the frame |
|---|---|---|
| Neck | 12 mm | 10 mm (excluding the boss faces) |
| Bulkhead | 17 mm | |
| Chin | 18 mm | |
| Cheeks | 35 mm | |
| Lamps | 43 mm | |
| Everything else | more than 50 mm | |

## Assumptions and guesses
- The solids are **outer shapes**. Real carbon parts would be moulded skins, not solid blocks.
- The lamp size is a placeholder until the lamps are chosen.
- The eye positions used for the viewing angles are guesses for a 1.8 m rider.
- The model inherits the clean model's accuracy: about ±2 mm on the frame, and "up" is not yet checked against the bike on its wheels.
- The boss positions are carried over from the earlier scan (fit to within about 1.2 mm median).
- The tyre and mudguard at full fork compression are not modelled. The pod bottom is about 60 mm above the top of the bottom yoke.
