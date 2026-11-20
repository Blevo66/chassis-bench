# Nav tower v3: one-piece carbon monocoque

Joel's pick after v1 (boxy) and v2 (separate side plates): a **single moulded shell**.
It uses the same coordinates as the clean frame model:
- Origin: on the steering axis, at the bottom of the head tube.
- X: to the right of the bike.
- -Y: forward.
- Z: up.
- Units: mm.

## The shell (`monocoque_carbon`)
- **Construction:** one lofted body through 13 rounded-rectangle sections, from the beak (Z 90) up to the cradle top (Z 470). It is hollow with a 3 mm skin and open at the bottom for wiring. The neck that bolts to the 4 M8 bosses is fused on as part of the same piece.
- **Size:** about 212 wide at the lamps and at the top, and about 172 wide at the waist behind the dash.
- **Cut-outs:** twin 85 mm lamp bores (lamps at X ±46, Z 153), a recess for the dash (133 x 99 x 53), and three side windows through both skins. The lower window shows the lamp cans.
- **Rear face:** follows the 35° lean plane. The dash sits in its recess, and the cheeseboard bolts on above it with 4 x M6 inserts on a 100 x 100 square.

## Clearance (clearance.json)
| Part | To the 40° lock sweep (forks, yokes, bars) | To the frame |
|---|---|---|
| Shell (closest point is the neck) | 12 mm | 11 mm |
| Lamps | 48 mm | |
| Everything else | more than 50 mm | |

## Notes and guesses
- The neck is modelled solid. In carbon it would be a hollow moulded section or a bonded alu insert.
- The lamp size is a placeholder.
- Rider eye positions are guessed. With them, the dash is about 61° below the eye line when standing.
- The tyre and mudguard at full fork compression are not modelled.
- For moulds: the shell splits naturally down the centre line (X = 0) into two half-moulds.
