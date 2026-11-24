# XL dash DOCK IDEA v1: removable head on a latched dock

An idea alongside the main pod (v3n stays the current design in `files/dash-pod-v3/` on its own branch). Joel 2026-11-24: "a pogo connector between the ESP32 screen and LiPo, and then the MOSFET board and GPS stay on a dock on the bike".

**Axes (all files):** mm, Z up, Y forward, X right, screen faces -Y, origin = centre of the cover glass at its front face. STEPs are single bodies except the assembly.

## Head (comes off the bike): 105.2 x 66.4 x 17.5 mm
- Waveshare ESP32-S3-Touch-LCD-3.5 + 1200 mAh LiPo (62 x 35 x 5). v3n pod was 33.5 deep.
- Front ring as v3n (glass pocket, chamfered rim, board arms with locating pins, M3 heat-sets). Back shell 3.5 deep, 1.8 skin, TPU seal and shadow line at the split, 4 x M3 x 10 from the back face (heads hidden when docked).
- **Pogo adapter board** 48 x 9 x 1.6 sits flush in a window in the back: 2x16 header onto the Waveshare J8 on the front, **18 gold (ENIG) pads, 2 x 9 at 2.54** on the back.
- **Hooks:** two 12 mm tongues at the bottom (X +/-31) with a 2 mm downward lip. **Latch tongue** at top centre with a barb on its right side.
- Flush 3 mm breather in the bottom, "XL125R DASH" deboss on the back.

## Dock (stays on the tower): 105.2 x 66.4 x 22.7 mm (+7 mm M5 bosses)
- Tub (front wall 3 mm) + back cover, TPU seal and shadow line at the split, 4 x M3 from the back.
- **MOSFET board** (assumed Fowecry 99 x 52, 10 mm terminals) on 3.6 mm standoffs off the front wall, components facing BACK so the terminals are reachable with the back cover off.
- **18 pogo pins** on a 34 x 10 carrier board behind the front wall, tips ~0.6 mm compressed when docked. **TPU ring** (print black TPU) in a 1 mm groove round them, 0.3 proud.
- **Latch:** sprung steel/printed bar behind the front wall; the head's barb pushes it aside and it snaps over. **Release:** flush oblong button in the TOP face drives a wedge that slides the bar 2 mm.
- ATGM336H GPS on a pad on the back cover, ceramic antenna under a 1.6 mm thinned patch of the top wall. 5 V buck pad beside it.
- Loom in through a flush TPU grommet in the back between the tapered M5 bosses (60 c-c, same as v3n so the same tower bracket fits).
- **Cap** (`dock-cap`): 4.5 mm cover with the same hooks and tongue, presses the TPU ring when the head is off.

## Pogo signals (all low current; 2 A loads never leave the dock)
IN1-8 (MOSFET triggers), 5V, 3V3, GND x2, RPM, brake sense, SDA, SCL (to MCP23017 in the left bar controller), GPS TX, GPS RX.

## Guesses (check before printing)
MOSFET board size and heights (replace with Joel's STEP), Waveshare back-side parts (sets head depth), J8 mating height, pogo pin part (none picked), GPS antenna 19 x 6 x 5, buck size, latch spring/travel (test print).

Not modelled: optional fail-safe on the dock to keep low beam + tail on with the head off.

Scripts: `src/dock1.py` (CadQuery 2.x; clash check prints zero overlaps apart from the board locating pins), `src/viewer.html`. Renders in `renders/`. Viewer + renders page: see the thread.
