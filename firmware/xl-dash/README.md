# XL125R body-loom box + dash firmware (v0.1)

ESP32 firmware for the "ESP32 8 Channel MOS Switch" board (eBay 820144839205, 122 x 87.5 mm), a 4" ST7796S 480x320 SPI TFT (LCDwiki MSP4020, no touch; 108 x 62 mm module) and a u-blox M10 GPS.

Screen note: the 480x320 frame is drawn in a 4-bit, 16-colour sprite (75 KB) because an 8-bit one (150 KB) is unlikely to fit in a plain ESP32 without PSRAM. If "sprite alloc FAILED" shows on the serial monitor, that is the first thing to look at.

**Status: written, NOT compiled or tested yet.** The build server could not reach the PlatformIO registry, so the first compile happens on your laptop. Expect a few small fixes on the first build.

Loom page this matches: https://claude.ai/artifact/7RfLhucct5pzpFFF62vzXr
Screen mock-up: https://claude.ai/artifact/HZPUvWeBmFoRdDcqrsdwYQ

## Files
| File | What's in it |
| --- | --- |
| `platformio.ini` | Board, libraries (TFT_eSPI, TinyGPSPlus) and the screen's SPI pins |
| `src/config.h` | **Every pin and setting.** Start here. |
| `src/main.cpp` | Buttons, outputs, RPM, GPS/odometer, dash screens, WiFi page |

## Before you flash anything
1. **Fix the 8 output pins in `config.h` (`PIN_OUT`).** The MOS board's PCB decides which GPIO drives OUT1 to OUT8; the numbers in there are placeholders. Get them from the board's print, the seller, or by tracing with a meter.
2. Check no other pin in `config.h` clashes with those 8. If they do, move the clashing input.
3. Change `AP_PASS` (WiFi password).

## Build and flash
1. Install VS Code + the PlatformIO extension (or `pip install platformio`).
2. Open this folder, plug the board in by USB-C, press Upload (or `pio run -t upload`).
3. Watch the serial monitor at 115200.

## How wiring maps to code
| Wire (loom page) | Pin | Code |
| --- | --- | --- |
| OUT1..OUT8 | `PIN_OUT[]` | `writeOutputs()` |
| Buttons 1-5 (P2) | 21, 22, 13, 14, 25 | `handleButtons()` |
| RPM pickup filter | 34 | `rpmISR()` / `updateRpm()` |
| Brake sense opto | 35 | `updateVolts()` sets `S.brake` |
| Volts divider 100k/22k | 33 | `updateVolts()` |
| GPS TX / RX | 16 / 17 | `updateGpsAndOdo()` |
| TFT SCK/MOSI/CS/DC, backlight | 18/23/5/4, 32 | `platformio.ini`, `drawScreen()` |

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
- Sparks per rev, shift light, gear ratios and voltage thresholds are guesses in `config.h`.
- Output test buttons on the WiFi page force outputs on; they reset when WiFi turns off.
- WiFi hotspot `XL-DASH` turns itself off after 10 minutes or above 5 mph.

## Ignition battery (wireless)

The engine loom stays completely separate. A small ESP32-C3 on the ignition pack (`firmware/ign-sender`) broadcasts its voltage, and current if an INA226 is fitted, over Bluetooth every ~5 s. The dash listens with a passive NimBLE scan and shows:

- **Ride screen:** `IGN 14.6V 72%` under the gear box, coloured green / amber / red.
- **System screen:** volts, %, current (live or "est") and rough time left.
- **IGN BATT LOW** flashing banner below `IGN_LOW_PER_CELL`.
- `IGN --` if nothing heard for 20 s. The engine is unaffected either way.

Set `IGN_LIFEPO4`, `IGN_CELLS`, `IGN_CAPACITY_MAH` and `IGN_ASSUMED_MA` in `config.h` for your pack. The defaults are guesses. The CDI is rated 16 V max, so use 3S Li-ion (12.6 V full) or 4S LiFePO4 (14.6 V full), never 4S Li-ion (16.8 V). Memory note: WiFi + Bluetooth + the 75 KB screen frame together are tight on a plain ESP32. If it runs out, the first fix is to stop the Bluetooth scan while the WiFi page is open.
