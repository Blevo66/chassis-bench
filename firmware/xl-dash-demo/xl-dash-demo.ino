// =====================================================================
//  XL125R dash: DEMO MODE  (Arduino IDE sketch)
//  Board: Waveshare ESP32-S3-Touch-LCD-3.5 (ST7796 480x320, FT6336 touch)
//
//  Tools menu settings:
//    Board ............ ESP32S3 Dev Module   (esp32 by Espressif 3.2.0, NOT 3.3.x)
//    USB CDC On Boot .. Enabled
//    Flash Size ....... 16MB (128Mb)
//    PSRAM ............ OPI PSRAM            <- needed, the frame buffers live there
//    Partition Scheme . any 16M option (e.g. "16M Flash (3MB APP/9.9MB FATFS)")
//  Libraries (same as Waveshare's examples):
//    GFX Library for Arduino 1.5.5, TCA9554 0.1.2. Nothing else.
//
//  What it does: plays a fake ride on a loop (rev up through the gears,
//  cruise, overtake, brake, stop) so you can watch the dash move.
//  Swipe left/right (or tap) to change page: RIDE, TRIP, SYSTEM.
//  If a GPS is wired (settings in dash_demo.h) and has a fix, the speed
//  comes from the GPS instead of the fake ride.
//
//  All the code is in the dash_demo.h tab. Settings are at the top of it.
// =====================================================================
#include <Arduino_GFX_Library.h>
#include <Wire.h>
#include "TCA9554.h"
#include "dash_demo.h"

void setup() { dashSetup(); }
void loop()  { dashLoop(); }
