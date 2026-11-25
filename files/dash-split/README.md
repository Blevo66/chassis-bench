# XL dash v4: SPLIT into a screen pod + brain box (2026-11-25)
Joel: v3t (all in one, 142 x 66 x 46) looked bulky -> light screen pod on the tower, "brain" under the tank in the frame triangle.

## Screen pod v7, CURRENT: screen centred, socket out the RIGHT SIDE (screen-pod-v7-centred/, src/pod7.py)
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

## Brain box v3, CURRENT (brain-box-v3/, src/brain3.py)
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
