// =====================================================================
//  XL125R dash v1 (Arduino IDE)
//  Board: Waveshare ESP32-S3-Touch-LCD-3.5
//
//  Tools menu: Board "ESP32S3 Dev Module" (esp32 core 3.2.0), USB CDC On Boot
//  Enabled, Flash 16MB, PSRAM "OPI PSRAM", any 16M partition scheme.
//  Libraries: GFX Library for Arduino 1.5.5, TCA9554 0.1.2.
//
//  Tabs: config.h = settings + pins (start here), dash.h = the code,
//  fonts.h = smooth fonts (generated, don't edit).
//
//  Buttons (left controller):
//    IND L / IND R  tap = on / cancel     hold = hazards on / off
//    HORN           sounds while pressed
//    LIGHTS         hold 3 s = headlight on (low) / off    tap = high / low (when on)
//                   DRL (OUT7) always on: full with headlight off, dimmed with it on
//    MODE           tap = flash high beam  hold = next page  (TRIP page: hold 3 s = reset trip A)
//  Swipe the screen (or tap) to change page too. Pages: RIDE, TRIP, SYSTEM, TEST.
// =====================================================================
#include <Arduino_GFX_Library.h>
#include <Wire.h>
#include <Preferences.h>
#include "TCA9554.h"
#include "config.h"
#include "dash.h"

void setup() { dashSetup(); }
void loop()  { dashLoop(); }
