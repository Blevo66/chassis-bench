# XL dash v2: screen for the split dash

The screen half of the split: Waveshare ESP32-S3-Touch-LCD-3.5 + GPS. The **brain box**
(`../xl-brain`) runs the buttons, outputs, RPM and brake and sends its state here over a
5-pin serial link (screen IO21 = RX from box, IO48 = TX to box). Pages, trips, odometer and
the clock live here (the GPS is in the screen pod).

`../xl-dash-v1` is the all-in-one version (buttons + MOSFETs on the screen) for testing
without a box.

**Status:** tested only in the PC simulator together with the box firmware
(`tools/host-preview/link-test.cpp`: 22 checks pass, including pulling the cable).

- Same Arduino settings as v1 (esp32 core 3.2.0, OPI PSRAM, GFX Library 1.5.5, TCA9554 0.1.2).
- Folder `xl-dash-v2` with `xl-dash-v2.ino`, `config.h`, `dash.h`, `fonts.h`.
- TEST page: buttons (from the box), held time, last action, outputs, "NO BOX" when the link is down.

Previews (simulator): `previews/test-page-with-box.png`, `previews/test-page-no-box.png`, `previews/ride.png`.
