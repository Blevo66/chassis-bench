# XL brain box (standalone)

Runs the bike on its own: left-bar buttons, indicators, headlight, DRL, tail, horn, RPM and
brake. The screen (`../xl-dash-v2`) is optional: it shows what the box is doing and handles
pages and trips. Unplug the screen and the box keeps working.

**Status:** compiled and tested together with the screen firmware in a PC simulator only
(`../xl-dash-v2/tools/host-preview/link-test.cpp`, 22 checks). Not yet run on real hardware.

## Arduino IDE
- Board: **ESP32S3 Dev Module** (esp32 core **3.2.0**), USB CDC On Boot: Enabled. No extra libraries.
- Folder `xl-brain` with `xl-brain.ino`, `brain_config.h`, `brain.h`.
- Settings and pins: `brain_config.h`. Bike-specific numbers are in its **BIKE** section.

## Wiring (pins are my picks for an ESP32-S3-DevKitC-1; change in brain_config.h if needed)

| ESP32-S3 pin | Goes to |
| --- | --- |
| IO4, 5, 6, 7, 15, 16, 17, 18 | MOSFET board IN1..IN8 (OUT1 IND L, 2 IND R, 3 LOW, 4 HIGH, 5 HORN, 6 USB, 7 DRL, 8 TAIL) |
| IO8 (SDA), IO9 (SCL), 3V3, GND | Left controller cable (MCP23017 board) |
| IO10 | RPM: coil round the HT lead, through its filter/conditioning circuit |
| IO11 | Brake: opto across the rear lamp (LOW = brake on) |
| IO12 (TX) | Screen IO21 (screen's RX) |
| IO13 (RX) | Screen IO48 (screen's TX) |
| 5V, GND | Buck converter output (also feeds the screen over the link cable) |

**Screen link, 5 pins:** 5V, GND, box TX -> screen RX (IO21), screen TX (IO48) -> box RX, second GND.

**Power in:** 12 V DC from the separate reg/rec. Suggested (not drawn yet): reverse-polarity
protection + TVS diode on the input, then the buck (5 V) and the MOSFET board supply.

**Bike connections:** only 12 V power and the HT-lead RPM coil. Everything else is on the
swappable loom.

## Serial link format
Text lines, NMEA style `$<body>*<XOR checksum>`:
- box -> screen, 20 Hz: `S,rpm,flags,btn,outs,mcpAddr,eventCount,held0..held4,lastEvent`
  (flags: 0 indL 1 indR 2 hazard 3 high 4 flash 5 horn 6 lightsOn 7 drl 8 brake 9 beam)
- box -> screen events: `E,PAGE` (next page), `E,TRIP` (reset trip A)
- screen -> box, 5 Hz: `P,page`

Open the box's Serial Monitor at 115200 to see `[button] ...` lines for every press.

## Not done yet
- Phone setup page (Wi-Fi) for the BIKE settings; "calibrate RPM at idle".
- Status LED on the box.
