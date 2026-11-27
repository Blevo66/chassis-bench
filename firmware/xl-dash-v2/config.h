// =====================================================================
//  XL125R dash v2 (screen for the split dash): SETTINGS. Start here.
//  Board: Waveshare ESP32-S3-Touch-LCD-3.5 + GPS. Talks to the brain box (xl-brain).
// =====================================================================
#pragma once

// ---- Demo or real -----------------------------------------------------
// 0 = REAL: GPS speed + everything the brain box sends.
// 1 = DEMO: the fake ride from the demo sketch (buttons still show on the Test page).
#define DEMO_MODE 0

// ---- Screen -------------------------------------------------------------
#define SPI_HZ 40000000          // 40 MHz is known good; 80 MHz may work
#define SCREEN_ROTATION 1        // 3 if upside down
#define TOUCH_SWAP_XY 1          // touch mapping (guess): flip TOUCH_FLIP_X if swipes go backwards
#define TOUCH_FLIP_X 0
#define TOUCH_FLIP_Y 1
#define NEEDLE_EASE_S 0.10f      // needle catch-up time, seconds
#define SPEED_EASE_S 0.18f
#define GHOST_TRAIL 1            // faded needles behind the real one
#define RETRO_STRIPES 0          // tricolour stripes in the background
#define STRIPE_ALPHA 150         // 0-255, strength of the big diagonal stripes

// ---- I2C bus (Waveshare fixed: SDA 8, SCL 7): touch, power chip, screen reset chip
#define I2C_HZ 400000

// ---- Link to the brain box (it runs buttons, lights, RPM and brake) ------------
// Box TX (its IO12) -> screen IO21, screen IO48 -> box RX (its IO13). Same J8 pins the
// RPM and brake used on v1.
#define LINK_RX_PIN 21
#define LINK_TX_PIN 48
#define LINK_BAUD 115200
#ifndef LINK_SERIAL
#define LINK_SERIAL Serial2
#endif
// Only used for labels on the TEST page (the box decides what the buttons do)
#define BTN_IND_L  0
#define BTN_IND_R  1
#define BTN_HORN   2
#define BTN_LIGHTS 3
#define BTN_MODE   4
static const uint32_t HOLD_MS = 700;         // match the box: test page turns amber at this
static const char *OUT_NAME[8] = {"IND L", "IND R", "LOW", "HIGH", "HORN", "USB", "DRL", "TAIL"};
enum OutIdx { O_IND_L = 0, O_IND_R, O_LOW, O_HIGH, O_HORN, O_USB, O_AUX, O_TAIL };

// ---- GPS (UART). GPS TX -> IO17, GPS RX -> IO18. Joel's: 9600 baud, works.
#define GPS_RX_PIN 17
#define GPS_TX_PIN 18
#define GPS_BAUD 9600
static const float GPS_STILL_MPH = 1.5f;      // below this shows 0 (kills GPS drift when stopped)

// ---- Dial, shift light, gearing (placeholders until measured) ----------------
static const float RPM_MAX = 11000;
static const float RPM_AMBER = 7000;
static const float RPM_SHIFT = 9500;
static const float GEAR_RPM_PER_MPH[6] = {0, 450, 300, 225, 180, 150};
