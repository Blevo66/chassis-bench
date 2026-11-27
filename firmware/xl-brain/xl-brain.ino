// =====================================================================
//  XL brain box (Arduino IDE)
//  Board: ESP32-S3-DevKitC-1 (Tools: "ESP32S3 Dev Module", esp32 core 3.2.0,
//  USB CDC On Boot Enabled). No extra libraries.
//
//  The box runs the bike's lights, indicators and horn on its own. The screen
//  is optional: it shows what the box is doing and handles pages and trips.
//  Tabs: brain_config.h = settings + pins (start here), brain.h = the code.
//
//  Buttons: same as the dash v1:
//    IND L / IND R  tap = on / cancel     hold = hazards on / off
//    HORN           sounds while pressed
//    LIGHTS         hold 3 s = headlight on (low) / off    tap = high / low (when on)
//                   DRL (OUT7) always on: full with headlight off, dimmed with it on
//    MODE           tap = flash high beam  hold = next page  (TRIP page: hold 3 s = reset trip A)
// =====================================================================
#include <Wire.h>
#include "brain_config.h"
#include "brain.h"

void setup() { brainSetup(); }
void loop()  { brainLoop(); }
