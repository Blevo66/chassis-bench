# XL dash pod v3: Waveshare ESP32-S3-Touch-LCD-3.5

Built around the real Waveshare CAD (from waveshareteam/ESP32-S3-Touch-LCD-3.5, `hardware/mechanical/ESP32-S3-Touch-LCD-3_5.stp`).

**Axes (all files):** mm, Z up, Y forward, X right. The screen faces -Y. The origin is the centre of the cover glass, just behind its front face.

## Size
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
