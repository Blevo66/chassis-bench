# XL dash pod v3: Waveshare ESP32-S3-Touch-LCD-3.5

Built around the real Waveshare CAD (from waveshareteam/ESP32-S3-Touch-LCD-3.5, `hardware/mechanical/ESP32-S3-Touch-LCD-3_5.stp`).

**Axes (all files):** mm, Z up, Y forward, X right. The screen faces -Y. The origin is the centre of the cover glass, just behind its front face.

## v3p (current): HangTon WS28 24-pin socket straight out of the back
Joel 2026-11-24: wants the WS28 on the unit, "straight out the back".
- **143.2 × 66.4 × 33.5 mm** (EXT 38). Socket centre X 64.6 (pod axes), right of the MOSFET board so the ~10 mm solder-cup stub has wire room; otherwise the pod would need ~11 mm more depth.
- WS28 type Z (seller's table): flange 36 × 36, 4 × Ø3.2 on 30 mm square, panel hole Ø28.5, M30 × 1, L 23, rear stub Ø27.8 × 9.8. Flange thickness 2.5 GUESSED. 1 mm TPU gasket (`xl-dash-pod-v3p-ws28-gasket.stl`), 4 × M3 × 10 + nyloc nuts.
- Grommet version v3o is in `v3o-grommet/`. Scripts `src/pod3p.py`, `src/lite3p.py`.

## v3o: flush TPU grommet, tapered back, single unit
Joel: not keen on the threaded gland boss; "all the plugs look huge" on such a small pod.
- **124.2 × 66.4 × 33.5 mm.** No plug on the pod. ~10 mm 17-core flylead out of the back through a **flush black TPU (95A) grommet**: 22 mm flange 0.3 mm below the back face, 15 mm neck, 18 mm retaining lip inside, 9.4 mm bore, 5 mm tail for glue-lined heat-shrink. Grommet is in the assembly STEP; print it separately.
- **Back cover ends taper in 1.5 mm** toward the back (top/bottom straight, so the GPS antenna pocket keeps its wall).
- **Plug lives in the nav tower:** HangTon WS28 24-pin 5 A (square-flange socket 36 × 36, M30 × 1, panel hole Ø28.5, 4 × Ø3.2 holes on a 30 mm square, 23 deep (9.8 behind flange); plug Ø34 × 56) — socket bolted through the tower, plug on the flylead end. 12 V and earth get 2 pins each.
- v3n (M20 gland boss) is in `v3n-gland/`. Scripts `src/pod3o.py`, `src/lite3o.py`.

## v3n: flylead through a cable gland, no panel plug
Joel 2026-11-24: AMPSEAL "way too big", picked a flylead through a sealed gland.
- **124.2 wide × 66.4 tall × 33.5 deep** (+6 mm gland boss / 7 mm mounting bosses). R8.7 corners all round.
- **Flylead:** one sheathed ~10 mm, 17-core cable out of the BACK, straight into the nav tower; plugs on its end live behind the tower. **M20 × 1.5 IP68 nylon cable gland** (6–12 mm cable, 24 AF hex; size TYPICAL, check yours) screws into a printed M20 × 1.5 thread in a 26 mm boss at X 52 / Z 13 (Fusion), so no locknut inside. Print the thread, or print the 18.5 mm tap-drill hole and run an M20 × 1.5 tap through.
- Polish kept from v3m: split shadow line, chamfered glass rim, tapered M5 bosses, flush breather (PTFE vent inside), "XL125R DASH" deboss.
- Clash check clean (gland thread overlaps its own printed thread by design).
- v3m (AMPSEAL 23 inside) is in `v3m-ampseal/`. Scripts `src/pod3n.py`, `src/lite3n.py`.

## v3m: real AMPSEAL 23 header, 5 mm deeper, polished
Joel: "make it a bit deeper, and drop the rounded corners right down on that end", then "make it look perfect and polished".
- **131.2 wide × 66.4 tall × 38.5 deep** (+7 mm mounting bosses). Plug end corners R2.5 (rest of the pod R8.7).
- **Real header:** TE 776228-1 (sealed AMPSEAL 23, vertical), from TE's own STEP (`parts/te-776228-1-ampseal23.stp`). Measured: socket 43.4 × 23.6 × 19 tall, flange 60.8 × 32.1 × 3.5 with **no screw holes**, body + solder tails 16 mm behind the flange.
- **Mounting:** flange INSIDE against the right wall on a 1 mm TPU gasket (`xl-dash-pod-v3m-plug-gasket`, print in **black** TPU). Header slides in sideways from the split into the back cover; a floor rib in the back cover and a rib under the front ledge press on the flange's long edges (0.3 mm squeeze, shows as a small overlap in the clash check) when the pod closes. Only the socket comes through: 0.2 mm gap, 0.8 mm chamfer.
- **Polish:** shadow-line reveal at the split, chamfered glass rim, tapered M5 bosses, flush 3 mm breather (stick a 12 mm adhesive PTFE vent over it inside; the cable boot is gone), "XL125R DASH" debossed on the back.
- Solder tails end about 7 mm short of the MOSFET board edge, with open space above and below for the wires to turn.
- v3l (plug size guessed) is in `v3l-plug-guess/`. Scripts: `src/pod3m.py`, `src/lite3m.py`.

## v3h (REJECTED by Joel, "looks shite"): chin under the pod for one sealed rectangular bulkhead plug
Joel wants all the loom wires through ONE rectangular bulkhead plug (OBD/ECU style) in the bottom.
- **105.2 wide × 33.5 deep**, now **93.4 tall** with the chin (27 mm chin, 72 mm wide, part of the back cover). Everything else as v3g.
- **Plug size is GUESSED** (sized for a TE AMPSEAL 23-way style header): panel cutout 56 × 20, 2 × M3 flange screws 60 c-c, body 54 × 18 × 22 deep. Set the real cutout once the part is picked.
- Pin count needed ~20–24: 12 V ×2, earth ×2, OUT1–8, RPM ×2, brake, 5 buttons + common.
- The chin opens up into the pod behind the split. Cable boot removed; breather vent moved to X −40.
- Files kept in `v3h-chin-rejected/`.

## 3D viewer
Spin it round on your phone: https://claude.ai/artifact/EH1iRSsUwUcDufBJbzJEgK (v3o and v3n, see-inside, explode). Renders: https://claude.ai/artifact/XFMFhj66m8xGHSTDTvJPC7

## v3l: wider pod, screen to the left, one bulkhead plug out of the right side
Joel: "just make the thing wider with the screen offset to the left".
- **131.2 wide × 66.4 tall × 33.5 deep.** The whole pod is 26 mm wider on the right; screen, Waveshare and MOSFET board stay where they were (screen centre is 13 mm left of the pod centre). No visor peak.
- **Side plug** on the right face, size GUESSED for an AMPSEAL 23-way style header: 56 × 20 cutout centred 17 mm behind the front face, so it straddles the front/back split (notch in both halves). 2 × M3 flange screws at 60 c-c into bosses in the back cover. The plug's own panel gasket seals the cutout; the TPU seal is broken there.
- Everything else as v3j (ATGM336H, ceramic antenna pocket, MOSFET board on the back cover, 4 corner screws). Clash check (`src/pod3l.py`): zero overlaps.
- v3j (105 wide, no plug) is in `v3j-no-peak-narrow/`; the side-block idea v3k is in `v3k-side-block-rejected/`.

## v3j: no visor peak
Joel: "get rid of the peak". Same as v3i otherwise: **105.2 × 66.4 × 33.5 mm**, ATGM336H GPS, ceramic antenna pocket in the top wall, MOSFET board on the back cover.

## v3k (REJECTED, `v3k-side-block-rejected/`): one sealed rectangular bulkhead plug out of the right side
Joel wants one bulkhead plug out of one side ("more universal going forward").
- There is no room inside: the MOSFET board fills the pod side to side (0.6 mm spare). So a 26 mm block is added to the right of the back cover: **131.2 wide** (screen no longer centred), same height and depth.
- Plug size GUESSED for an AMPSEAL 23-way style header: 56 × 20 cutout, 2 × M3 flange screws 60 c-c, body 54 × 18 × 22 deep. Wires pass into the pod through a window in the old side wall.
- Front ring and seal are the same as v3j. Clash check (`src/pod3k.py`): zero overlaps.

## v3i: GPS ceramic antenna, with the visor peak (now in `v3i-peak/`)
Joel ordered the ATGM336H GPS (QuveX, Amazon): 12 × 15 mm board, VCC/GND/TX/RX/PPS, active ceramic antenna on an IPX lead.
- Same pod as v3g: **105.2 × 66.4 × 33.5 mm**, MOSFET board + GPS on the back cover, 4 × M3 × 25 corner screws.
- **Antenna** (size ESTIMATED from the listing photos: ~19 × 6 × 5 mm) lies flat under the top wall, facing the sky, behind the MOSFET board's top terminal strip. The top wall is thinned to 1.6 mm in a 22 × 9 pocket over it (outside unchanged). Re-check against the real part.
- **GPS board** sits on a 10 × 14 pad on the back floor at the right end of the terminal-strip gap.
- v3g (thin FPC antenna) is in `v3g-fpc-antenna/`. Clash check (`src/pod3i.py`): zero overlaps.

## v3g: MOSFET board and GPS on the back cover
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

## v3q: Joel's real MOSFET board (2026-11-24)

Built from Joel's own STEP of the Fowecry 8-ch board (`parts/fowecry-mosfet-board-joel.step`). Script `src/pod3q.py`.

**Measured from Joel's model (facts):** PCB 99 x 52 x 1.5, mounting holes 91 x 44 (was 90 x 43), tallest screw terminals 14.1 mm above the PCB (I had guessed 10), input strip 9.5-10.5, jumper headers ~8.5-9.0, MOSFETs/optos 2.5-4.5.

**Changes from v3p:**
- Back 4.3 mm deeper: pod is now 143.2 x 66.4 x **37.8** mm (v3p 33.5). Terminals clear the back wall by ~0.6 mm.
- MOSFET standoffs moved to 91 x 44.
- LiPo: the 62 x 35 PKCell 1200 no longer fits between the terminal strips (gap ~33 mm). Drawn a **500 mAh ~30 x 36 x 5** cell lying on the jumper headers, left side, ~0.7 mm under the back wall. Cell size is a guess at a typical 500 mAh pouch.
- GPS receiver stuck straight to the back wall (right of centre); ceramic antenna pocket moved to the top wall above the WS28 socket, clear of the 14 mm terminals.

**Guesses / unconfirmed:** which terminal strip is at the top (I put the 14 mm strip at the top), LiPo size, GPS sizes (arrives 25 Nov).

Renders: `renders/v3q-*.png`. Old v3p files in `v3p-guessed-mosfet/`.

## v3r: two M12 round plugs (2026-11-25, current)

Joel: the WS28 "looks ridiculous" -> picked two small M12 plugs. Script `src/pod3r.py`. Pod **132.2 x 66.4 x 37.8 mm** (v3q 143.2). Same real MOSFET board, LiPo, GPS as v3q; antenna pocket shifted to X 51-71.

Two front-mount M12 panel sockets stacked on the back at the right end (X 61, Y +/-13.5), 16.2 mm panel holes. **Socket and plug sizes are TYPICAL M12 values, not a chosen part** (M16x1.5 panel thread, ~20 mm hex, ~13 mm body + solder cups inside). Plugs drawn as straight moulded cordsets; right-angle ones would stick out ~30 mm less.

Pin split (ratings are typical M12 A-coded catalogue values, check the part you buy):
- Top, 8-pin (~2 A/pin): OUT1-8.
- Bottom, 12-pin (~1.5 A/pin): 12 V x2, power earth x4 (lamp current returns through the board), signal earth (controller + RPM screen), brake, RPM, controller 3V3, SDA, SCL.

Old WS28 version in `v3q-ws28/`.

## v3s: LiPo between the boards, right-angle J8 plug (2026-11-25, current)

Same shells as v3r (132.2 x 66.4 x 37.8, two M12 sockets). Script `src/pod3s.py`.
- **LiPo** moved (Joel's CAD): 500 mAh, ~30 x 36 x 5 (typical size, guess), long side vertical, flat in the ~11 mm gap between the Waveshare PCB and the MOSFET PCB, sat just above the J8 plug. Clash check clean.
- **J8 plug**: 2x16 2.54 right-angle male header (snapped from 2x20/2x40), wires soldered to the tails pointing up the pod, printed hood over it filled with glue. Drawn as its envelope (z -12.95..-18.2, under 6 mm to the MOSFET PCB). A Dupont housing does NOT fit (needs ~12-14 mm).
- **M12 sockets**: Joel picked Amazon Hamadap 2-pack M12 12-pin A-coded male front-mount, potted pigtail, IP67. Still drawn at typical size (16.2 hole) until the listing's panel hole size is known.
