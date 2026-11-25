# XL dash v4: SPLIT into a screen pod + brain box (2026-11-25)
Joel: v3t (all in one, 142 x 66 x 46) looked bulky -> light screen pod on the tower, "brain" under the tank in the frame triangle.

## RS M12 link, CURRENT (2026-11-25): screen pod v8 + brain box v7
Joel picked RS PRO pre-wired, shielded, front panel-mount M12 8-pin A-coded sockets with an M16x1.5 clamp nut:
- **Screen pod v8** (screen-pod-v8-rs-m12/, src/pod8.py): male **RS 250-0742** in the right side wall, flange outside, nut inside. Its lead S-bends down under the board (gap to the Waveshare parts ~2 mm, checked against the board STEP).
- **Brain box v7** (brain-box-v7-rs-m12/, src/brain7.py): the plain 137 x 94.5 x 38 box (option A) with the female **RS 250-0736** beside the AMPSEAL. The female sits on the box because it carries 5 V out, so its contacts are the shrouded ones.
- Cable: **RS 877-1208**, 2 m, RIGHT-ANGLE female at the screen pod, straight male at the brain box, 6.4 mm, unshielded, coding not stated (Joel wants the 90 deg end at the screen). Was 283-4972 (1 m straight).
- Shared socket model: src/rsm12.py. ONLY the M16x1.5 thread is from RS. Flange, nut, body length and plug sizes are GUESSES: measure the real parts and change the numbers there, then re-run pod8.py / brain7.py.
- No clashes in either box. Renders: renders/v8-*.png, renders/v11b-*.png.

## Screen pod v7: screen centred, socket out the RIGHT SIDE (screen-pod-v7-centred/, src/pod7.py)
- Joel 2026-11-25: 'shrink the length slightly and make the screen central'.
- 104.8 x 66.4 x 26.5 mm (3.5 mm extra each side of the screen), ~56 g PETG.
- Socket centre y -13 / z -14.5, tucked behind the board's thin right edge (board STEP: only 4.5 deep for x>40, 1.4 for x>46).
  Rear body 5 mm clear of the board parts; leads run straight in under the parts. LiPo moved to x 4..40.

## Screen pod v6 (superseded): Hamadap socket out the RIGHT SIDE, no visor (screen-pod-v6-side-plug/, src/pod6.py)
- Joel 2026-11-25: 'make the cable come out the side, lose the visor for now'.
- 111.8 x 66.4 x 26.5 mm (+7 mm M5 bosses, 60 c-c), ~60 g PETG. Right side extended 14 mm to hold the socket.
- Socket centre y -14 / z -13.6, hex flats top/bottom (19 AF est.) in the 20.8 mm inner depth; wall seat 0.3 deep (2.8 mm panel).
- Socket rear 5 mm clear of the board edge for the leads to turn. Hex/nut/length split still ESTIMATES from Joel's photo.

## Screen pod v5 (parked): sun visor (screen-pod-v5-visor/, src/pod5.py)
- v4c + the outer wall carries on past the glass as a hood: 13 mm proud at the top, fading to nothing 40 mm down the sides. Softer 2.2 back edge.
- Body still 97.8 x 66.4 x 26.5 behind the glass; ~55 g PETG. Internals and Hamadap socket unchanged from v4c.
- Wiring: screen-pod-wiring.html (also published as an artifact).

## Screen pod v4c: Hamadap M12 12-pin back-mount socket (screen-pod-hamadap/, src/pod4c.py)
- 97.8 x 66.4 x 26.5 mm (+7 mm M5 bosses, 60 c-c). ~50 g PETG shell (solid estimate). 4.5 mm thinner than v4b.
- Socket = Joel's Amazon Hamadap M12 12-pin A-coded back-mount pair (screws in from inside, M16 thread through a 16.2 hole in the flat back lid
  at x -20 / y -2). Socket body 5.2 mm clear of the board, so its moulded leads must bend within ~5 mm.
- ESTIMATES read off his listing photo: hex/nut 19 AF, how the 21 mm body splits either side of the lid, plug length.
- LiPo 7.7, GPS 10.6, antenna 8.5 mm clear.

## Screen pod v4b (superseded): plug out the back (screen-pod-back-plug/, src/pod4b.py)
- 97.8 x 66.4 x 31 mm (+7 mm M5 bosses, 60 c-c, now 18 mm above centre). ~56 g PETG shell (solid estimate).
- M12 8-pin through the flat back LID at x -20 / y -2 (left of centre, looking at the back from behind it's on the right), behind the patch where the
  Waveshare's back-side parts are only 9.8 mm deep (from its STEP). Socket tip 3.7 mm clear of the board.
- LiPo moved right, GPS receiver left, antenna under the top wall.

## Screen pod, side-plug version (screen-pod/)
- 113.8 x 66.4 x 26.5 mm (+7 mm M5 mount bosses on the back, 60 c-c as before). ~61 g of PETG shell (solid estimate).
- Waveshare ESP32-S3-Touch-LCD-3.5 + 500 mAh LiPo + ATGM336H GPS + ceramic antenna (antenna size estimated).
- Deep front ring holds everything; flat 2.5 mm back lid with TPU seal, 4x M3.
- ONE 8-pin M12 A-coded socket on the RIGHT side face (Joel said "M14", read as M12). Typical M12 sizes, not a chosen part.
- Board-plug STEP of the Waveshare is in ../dash-pod-v3/parts (assembly here has no board).

## Brain box v5: AMPSEAL in the END, flange INSIDE (brain-box-v5-internal-flange/, src/brain5.py)
- Joel 2026-11-25: 'the flange sits internally'. Header fits from inside as TE intends: flange rim on a 1 mm TPU gasket against the
  end wall's inner face, printed retainer behind it on 4 standoffs (M3 heat-sets). Shroud pokes ~15 mm out of the end.
- 152 x 82 x 38 mm (taller to fit the 32.1 flange inside), ~128 g PETG. Board, PCA9685, buck as v4.
- v5b (Joel: 'screen plug out the other wall, in the space next to the 12 V in'): Hamadap M12 moved to the FAR END wall, centred
  across (MY=0) until we know which side the board's VIN terminal is; 8 mm between socket body and board end. Box +15 long.
- v5c (Joel: 'shrink the width'): 70 wide (was 82). Retainer is now a plate behind the flange with two feet screwed DOWN into
  floor bosses (short M3 heat-sets), so nothing sits outside the 60.8 flange. Lid screws moved to x 29 / L-6, y +-27.5. ~114 g.
- v5d: M12 slid 14 mm to the -y side (Joel: the 12 V in is the big terminal on the side opposite the row of output terminals),
  hex turned so its flats face the side walls.
- v5e (Joel: 'no, try adding a lump on one side next to the AMPSEAL plug'): M12 now in the SAME end as the AMPSEAL, in a hollow
  27 x 24.5 mm lump on the -y side (roof at rim height, open into the main cavity). Box back to 137 long; 94.5 wide over the lump,
  70 elsewhere. M12 plug 3 mm from the (guessed) AMPSEAL plug envelope. Far lid screws moved to y +-31 to clear the board.
- v5f (Joel: 'make the lump more integrated'): one plan outline for base, lid and seal. Bulge runs full height under the lid,
  27 mm long at the plug end then tapers back into the side over 40 mm; outside corners R4, inside corner R8.

## Brain box v4 (superseded, flange outside): AMPSEAL in the END, free-standing (brain-box-v4-end-plug/, src/brain4.py)
- Joel 2026-11-25: 'make the ampseal plug go in the end of the unit' + 'ignore living in the triangle' (no frame fit any more).
- 132 x 82 x 33 mm, ~105 g PETG. AMPSEAL in the x=0 end wall, mounted from outside (flange + 1 mm TPU gasket + printed retainer, 4x M3 heat-sets).
- 10 mm wire-bend gap behind the AMPSEAL tails, then the MOSFET board (99 long) on 7.5 mm standoffs; PCA9685 and buck under it.
- Hamadap M12 in the side wall 24 mm from the far end, its body in the strip beside the board (2 mm clear of the board edge).
- Flat lid with a 1.5 mm TPU ring in a 1.2 mm groove (0.3 squeeze), 4 corner M3 screws.

## Brain box v3 (superseded, triangle fit) (brain-box-v3/, src/brain3.py)
- Joel 2026-11-25: 'the plug on the control box doesn't have to be flush anymore so it can stick out'.
- AMPSEAL 776228-1 mounted from OUTSIDE: flange + 1 mm TPU gasket on the wall's outer face, printed retainer frame with 4 legs, M3 into heat-sets
  in bosses inside the wall. Shroud + flange stick out ~23 mm; only the 16 mm rear body is inside (window 61.4 x 24.7 in the wall).
  NOTE: TE's rim seal is meant for panel-from-the-front; here the flat gasket behind the flange does the sealing (my design, untested).
- 105 x 89 mm (was 110 across), 33 tall at the plug end stepping to 29 (was 40/29). ~88 g PETG (was ~139). Buck moved under the MOSFET board.
- Frame fit (clean model, XOFF -15.5 to keep it centred): 2.5 under, 9.6 over, 3.0 in front.

## Brain box v2 (superseded) (brain-box-v2/, src/brain2.py)
- 2026-11-25: M12 swapped to the same Hamadap 12-pin back-mount socket as the screen pod (sizes estimated from Joel's photo). Plug end stays ~40 mm tall: the AMPSEAL flange alone is 32 mm.
Joel: slim it behind the plugs. 105 x 110 footprint; 40 mm tall only over the plug end (first 40 mm across the box), 45 deg ramp,
then 29 mm. MOSFET board on 7.5 mm standoffs with the PCA9685 (headers not fitted) lying under it; 5 V buck on the floor behind the plugs.
Stepped 2.5 mm lid; TPU seal swept along the stepped rim (it runs down the 45 deg ramp in the side walls so the lid screws still squeeze it).
Screen link plug: Joel's Amazon Hamadap M12 12-pin pair is fine (1 A/pin, link draws ~0.5 A); its real sizes still needed.

## Brain box v1 (brain-box/)
- 105 long x 110 wide x 40 tall, sits in the frame triangle on the brace slope (15.2 deg), front-bottom corner 144 mm behind
  the steering axis / 75.5 below the head-tube bottom (clean frame model coords). Fit check vs the clean model: ~2.5 mm all round
  (scan may read ~1.5 mm fat per side). Box sticks out ~60 mm left of the frame centreline incl. plug side.
- Joel's Fowecry MOSFET board flat on the floor; TE AMPSEAL 23 straight header 776228-1 FLUSH in the LEFT wall (thick wall round
  the shroud, 1 mm TPU gasket, printed retainer frame with 4x M3); wires solder straight to the pins (~10 mm to the board).
- M12 8-pin socket for the screen cable beside it on the same face. PCA9685 + 5 V buck on the lid underside (typical sizes).
- Both plugs point LEFT (my pick, not confirmed). Mating plug sizes are guesses.
- Mounting to the frame NOT designed yet (straps/rubber to brace or tabs to welded bosses: Joel to choose).

## Link screen <-> box (my plan, not built)
5 V, GND, SDA, SCL, RPM, brake (+2 spare) on the M12. PCA9685 in the box drives the 8 MOSFET inputs over I2C (also gives tail PWM).
Firmware needs PIN_OUT -> PCA9685 channels. Left-bar controller (MCP23017) shares the I2C bus.

## Unknowns
Room sideways under the tank (tank, coil, cables), which side the plugs should face, how the box mounts.
