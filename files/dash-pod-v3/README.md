# XL dash pod v3: Waveshare ESP32-S3-Touch-LCD-3.5

Built around the real Waveshare CAD (from waveshareteam/ESP32-S3-Touch-LCD-3.5, `hardware/mechanical/ESP32-S3-Touch-LCD-3_5.stp`).

**Axes (all files):** mm, Z up, Y forward, X right. The screen faces -Y. The origin is the centre of the cover glass, just behind its front face.

## v3h (REJECTED by Joel, "looks shite"): chin under the pod for one sealed rectangular bulkhead plug
Joel wants all the loom wires through ONE rectangular bulkhead plug (OBD/ECU style) in the bottom.
- **105.2 wide × 33.5 deep**, now **93.4 tall** with the chin (27 mm chin, 72 mm wide, part of the back cover). Everything else as v3g.
- **Plug size is GUESSED** (sized for a TE AMPSEAL 23-way style header): panel cutout 56 × 20, 2 × M3 flange screws 60 c-c, body 54 × 18 × 22 deep. Set the real cutout once the part is picked.
- Pin count needed ~20–24: 12 V ×2, earth ×2, OUT1–8, RPM ×2, brake, 5 buttons + common.
- The chin opens up into the pod behind the split. Cable boot removed; breather vent moved to X −40.
- Files kept in `v3h-chin-rejected/`.

## v3g (current again): MOSFET board and GPS on the back cover
Joel's assembly plan: screen and processor in the front ring, MOSFET board and GPS on the back cover, so the two halves come apart as two units.
- **Same size: 105.2 × 66.4 × 33.5 mm.** LiPo and GPS receiver still sit between the terminal strips (jumpers removed and bridged to H).
- **MOSFET board** screws down onto 4 standoffs in the back cover with **4 × M3 × 6** from the inside, into M3 heat-set inserts in the standoff tops (holes 90 × 43).
- **GPS receiver** sticks to a small pad on the back floor; the FPC antenna stays on the top wall.
- **Pod closes with 4 × M3 × 25** from the back, in corner tubes just outside the MOSFET board's edges, into M3 heat-sets in the front ring's corner posts (at ±46.7, ±28.6).
- **Header plug** stays on the Waveshare. Give its pigtails a slack loop so the back can open like a book. When closed, the MOSFET PCB still sits just behind the plug and stops it backing off.
- All MOSFET board heights are still GUESSED from photos. Clash check (`src/pod3g.py`): zero overlaps.
- v3f (through-screw version) is in `v3f-through-screws/`.

## v3f: thinner, LiPo between the terminal strips
Joel's idea: the LiPo sits in the gap between the MOSFET board's two screw-terminal strips instead of behind them.
- **Outside: 105.2 × 66.4 × 33.5 mm** (was 44.2 in v3e). Same width and height, same screws and front ring layout.
- **MOSFET board model (GUESSED heights from listing photos):** two terminal strips ~10 mm tall along the top and bottom edges, optos/MOSFETs ~3.5 mm in the middle. Measure when it arrives.
- **Needs the yellow jumpers removed and bridged to H with solder**, because they sit in the gap.
- **PKCell 1200 mAh LiPo** (62 × 35 × 5) lies on the low parts in the gap (gap ~36 mm vs LiPo 35 mm, guess). Put Kapton tape under it.
- **GPS receiver** (guess 12 × 25 × 4) sits in the same gap at the right end; the FPC antenna stays along the top wall.
- A smaller LiPo would not make it thinner: the terminal strips set the depth. Soldering wires straight to the board instead of using the terminals could save roughly another 6 mm (guess).
- Exit boot and vent at Z −24. Clash check (`src/pod3f.py`): zero overlaps.
- The 44 mm v3e files are in `wide-44mm/`.

## v3e: wider for the real MOSFET board
Joel picked the **Fowecry 8-ch opto MOSFET board, 3.3 V version** (Amazon B0H9RL4SFW): 99 × 52 mm, holes 90 × 43 c-c Ø3.2, LR7843 MOSFETs, about 60 W per channel per the listing. Joel chose to widen the pod and keep everything in one box.
- **Outside: 105.2 × 66.4 × 44.2 mm.** The side bezel is now 6.2 mm; the top and bottom are still 2.5 mm.
- **MOSFET board** sits right behind the screen board, with its terminals facing the back cover so you can wire it with the cover off. Its PCB also holds the header plug in.
- **Four M3 × 30 screws** go from the back cover, through the MOSFET board's own holes, into heat-set inserts in the front ring. They clamp the board and close the pod.
- **Component height behind the MOSFET PCB is GUESSED at 15.4 mm.** Measure it when the board arrives.
- **Behind that:** the PKCell 1200 mAh LiPo, plus the GPS receiver (guess) and flat FPC antenna along the top.
- **Files:** now in `wide-44mm/`.
- **Older versions:** the 98 mm-wide v3c/v3d files are in `narrow-98mm/`.
- **Clash check** (`src/pod3e.py`): zero overlaps.

## v3c: MOSFET board inside, no GPS hump
Joel wanted the MOSFET board in the pod and didn't like the GPS hump.
- **Depth: 41 mm** to the back face (plus the 7 mm mounting bosses).
- **Inside, front to back:** the Waveshare board, then the 8-ch MOSFET module (GUESS 79 × 44 × 18, sitting above the header plug), then the PKCell 1200 mAh LiPo (62 × 35 × 5, real size).
- **GPS (v3d, current assembly):** inside the pod, with no lump. A thin flexible FPC GPS antenna (~40 × 15 × 0.3, 1575 MHz, u.FL) is stuck to the inside of the back cover's top wall, and a small u.FL receiver board (GUESS 25 × 12 × 4) sits behind the module at the top. The LiPo moved down to make room. The shells are unchanged from v3c, so the `xl-dash-pod-v3c-*` part files are still current, and `xl-dash-pod-v3d-assembly.step` shows the new layout.
- **Exit boot and vent:** moved to Z −28 on the underside.
- **Files:** `xl-dash-pod-v3c-*`. The 28 mm version with the hump is in `slim-28mm-gps-hump/`, and the 50 mm version is in `deep-50mm/`.
- **Clash check** (`src/pod3c.py`): zero overlaps.

## Slim version (v3b)
Joel thought 50 mm was too deep. The MOSFET module, buck and MCP23017 now live in the loom near the tower, and only thin signal wires come into the pod. The GPS sits in a hump on top of the visor, with its antenna facing the sky and a separate printed lid (`xl-dash-pod-v3b-gps-lid`).
- **Depth: 28 mm** to the back face (plus the 7 mm mounting bosses).
- Inside: the board, the header plug, and Joel's PKCell 1200 mAh LiPo (62 × 35 × 5, real size from The Pi Hut).
- Files are now in `slim-28mm-gps-hump/`.
- Clash check (`src/pod3b.py`): zero overlaps.

## Size (first, 50 mm deep version)
- Outside: 97.8 wide × 66.4 tall. Depth is 50 to the back face, plus the 11 mm visor and the 7 mm mounting bosses.
- **Bezel:** 2.5 mm plastic wall plus a 0.2 mm gap round the glass. The rest of the border is the glass's own black print (about 9.5 mm at the sides and 6 mm at the top and bottom, per Waveshare's drawing).

## Parts
| File | What |
|---|---|
| `xl-dash-pod-v3-front.step/.stl` | Front ring. A pocket takes the 92.44 × 61.0 × 1.1 mm cover glass, which sits 0.3 mm below the face on a 0.3 mm glue bed (silicone or Sikaflex). Four arms with Ø1.7 pins locate the board's 4 M2 holes (72 × 48.5). It has the visor and 4 corner bosses for M3 heat-set inserts. |
| `xl-dash-pod-v3-back.step/.stl` | Back cover. It has a TPU seal groove, 4 M3 counterbored screw tubes, two fingers that hold the 2×16 header plug home, an exit boot (Ø10 bore) and a breather-vent boss (Ø8) on the underside, and 2 M5 heat-set mounting bosses on the back (60 mm c-c, as v1/v2). |
| `xl-dash-pod-v3-seal.step/.stl` | Gasket, printed in TPU. |
| `xl-dash-pod-v3-assembly.step` | Everything in position. The board is simplified, so import Waveshare's own STEP for full detail. |

## Inside: GUESSED sizes (redraw when the parts arrive)
- 8-ch MOSFET module: 80 × 44 × 18, flat against the back
- MCP23017 module: 28 × 22 × 5
- LiPo, about 1000 mAh: 48 × 28 × 8
- Pololu D24V10F5 buck: 18 × 13
- BN-220 GPS: 22 × 20 × 6, against the top wall under the visor
- Header plug: 42 × 6 × 10

The clash check in `src/pod3.py` found zero overlaps between the shell, the real board and these blocks.

## Notes
- The board's USB-C faces the right-hand wall and can't be reached with the cover on. Update the firmware over Wi-Fi (OTA), or through the header's USB pins (U_N / U_P).
- Header J8 (2×16, 2.54 mm, female): the free pins with no camera fitted are IO17, 18, 21, 38–42 and 45–48. It also carries TXD/RXD, I2C, VBUS (5 V in) and VBAT.
