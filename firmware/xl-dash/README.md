# XL125R body-loom box + dash firmware (v0.2, Waveshare S3)

Runs on the **Waveshare ESP32-S3-Touch-LCD-3.5** (ESP32-S3R8, 16 MB flash, 8 MB PSRAM, 3.5" 480x320 ST7796 IPS, FT6336 touch, AXP2101 + LiPo), driving the **Fowecry 8-ch opto MOSFET board (3.3 V version)**, with a UART GPS and an MCP23017 for the left-bar buttons.

Screen pins, the reset line (pin 1 of the board's TCA9554 expander) and the I2C bus are taken from Waveshare's own BSP and Arduino examples (waveshareteam/ESP32-S3-Touch-LCD-3.5).

**Status: written, NOT compiled or tested yet.** The build server can't reach the PlatformIO registry, so the first compile happens on your laptop. Expect a small fix or two on the first build.

Loom page this matches: https://claude.ai/artifact/7RfLhucct5pzpFFF62vzXr

## Files
| File | What's in it |
| --- | --- |
| `platformio.ini` | Board settings (16 MB flash, OPI PSRAM, USB CDC), libraries, screen pins |
| `src/config.h` | **Every loom pin and setting.** Start here. |
| `src/main.cpp` | Buttons, outputs, RPM, GPS/odometer, dash screens, WiFi page |

## Build and flash (first time)
1. Install **VS Code**, then the **PlatformIO IDE** extension (Extensions tab, search "PlatformIO").
2. File > Open Folder > `firmware/xl-dash` (download the repo as a zip from GitHub, branch `claude/project-thread-wrhr9z`, if you don't use git).
3. Plug the Waveshare in by USB-C. Click the **arrow (Upload)** in the blue bar at the bottom. The first build downloads the ESP32 tools, which takes a while once.
4. If upload can't find the board: hold **BOOT**, tap **RESET** (or unplug/replug), let go of BOOT, then upload again.
5. Click the **plug icon (Serial Monitor)** to see messages at 115200.
After the first time, updates can go over Wi-Fi: join `XL-DASH`, open 192.168.4.1, upload `.pio/build/xl-dash/firmware.bin`.

## First run on the bench (no loom needed)
- The dash should show the Ride page. **Tap the screen** to change page (Ride, Trip, System).
- Join Wi-Fi `XL-DASH` (password in `config.h`, change it) and open 192.168.4.1 to toggle each output.
- "MCP23017 not found" on the serial monitor is normal until you fit one.
- If colours look like a photo negative, delete `TFT_INVERSION_ON` in `platformio.ini`. If red and blue are swapped, add `-D TFT_RGB_ORDER=TFT_RGB`.

## Wiring to the Waveshare header (J8)
| Wire | GPIO | Code |
| --- | --- | --- |
| MOSFET IN1..IN8 | 38, 39, 40, 41, 42, 45, 46, 47 | `PIN_OUT[]`, `writeOutputs()` (OUT8 = tail PWM) |
| MOSFET VCC / GND (10-way block) | 3V3 / GND | jumpers on **H** |
| RPM pickup filter | 21 | `rpmISR()` |
| Brake sense opto | 48 | `readBrake()` |
| GPS TX -> / <- GPS RX | 17 / 18 | `updateGpsAndOdo()`, set `GPS_BAUD` |
| MCP23017 SDA / SCL (address 0x27: A0-A2 high) | 8 / 7 | `mcpRead()`; buttons on GPA0-4 |
| Screen, touch, SD, audio | fixed by Waveshare | `platformio.ini` |
45 and 46 are boot-strapping pins that must be LOW at power-up; the opto inputs hold them low, so they are only used as outputs.
There is no bike-voltage input any more: the AXP2101 says when the 5 V feed drops (dash then runs on its LiPo) and the odometer is saved then.

## Button behaviour
| Button | Tap | Hold (0.7 s) |
| --- | --- | --- |
| Ind L / R | on / cancel | hazards |
| Horn | sounds while pressed | - |
| Lights | high / low | flash high while held |
| Mode | next screen | reset trip A |

## Known gaps / guesses
- Clock shows UTC from GPS (no BST offset yet).
- GPS runs at its default rate; 10 Hz needs a one-off setting (u-center, or a command added later).
- Sparks per rev, shift light and gear ratios are guesses in `config.h`.
- AXP2101 registers (5 V present, LiPo volts/%) come from the XPowersLib register map, not yet checked on the board.
- The screen redraws the whole frame (~16-20 fps at 40 MHz SPI). Try `SPI_FREQUENCY=80000000` if it looks steppy.
- Output test buttons on the WiFi page force outputs on; they reset when WiFi turns off.
- WiFi hotspot `XL-DASH` turns itself off after 10 minutes or above 5 mph.

## Ignition battery (wireless)

The engine loom stays completely separate. A small ESP32-C3 on the ignition pack (`firmware/ign-sender`) broadcasts its voltage, and current if an INA226 is fitted, over Bluetooth every ~5 s. The dash listens with a passive NimBLE scan and shows:

- **Ride screen:** `IGN 14.6V 72%` under the gear box, coloured green / amber / red.
- **System screen:** volts, %, current (live or "est") and rough time left.
- **IGN BATT LOW** flashing banner below `IGN_LOW_PER_CELL`.
- `IGN --` if nothing heard for 20 s. The engine is unaffected either way.

Set `IGN_LIFEPO4`, `IGN_CELLS`, `IGN_CAPACITY_MAH` and `IGN_ASSUMED_MA` in `config.h` for your pack. The defaults are guesses. The CDI is rated 16 V max, so use 3S Li-ion (12.6 V full) or 4S LiFePO4 (14.6 V full), never 4S Li-ion (16.8 V). Memory note: WiFi + Bluetooth + the 75 KB screen frame together are tight on a plain ESP32. If it runs out, the first fix is to stop the Bluetooth scan while the WiFi page is open.


## Rear light: one LED, tail and brake

One two-wire LED lamp does both. It's dim as a tail light and goes full brightness on the brake.

```
 fused +12V ──► lamp + ── LED lamp ── lamp − ──┬──► OUT8 (PWM, dim tail)
                                               ├──► front brake switch ──► earth
                                               └──► rear brake switch ───► earth
 opto: +12V ─ 2k2 ─ LED ─► lamp −     (output to GPIO35 with 10k pull-up to 3.3V)
```

- OUT8 PWMs the lamp at `TAIL_DUTY` (20%, guess) for the tail.
- The brake switches short lamp − straight to earth, in parallel with OUT8. Pressing the brake lights it at full brightness **with or without the ESP32 running**. That's the fail-safe.
- The brake switches must be two-wire with an insulated body, not earthed through the bike.
- `readBrake()` calls it "brake" when lamp − stays at earth for a whole PWM period. That's why `TAIL_DUTY` must stay well under 100%.
- If the ESP32 is dead you lose the tail light, but not the brake light.
- **Check on the bench:**
  - The lamp must dim cleanly on PWM. A plain LED-plus-resistor lamp should. One with its own constant-current driver might flicker or refuse to dim.
  - The MOS board must switch cleanly at `TAIL_PWM_HZ`. If it doesn't, drop it to 200–500 Hz.
