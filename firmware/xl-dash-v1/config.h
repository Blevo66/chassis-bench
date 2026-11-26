// =====================================================================
//  XL125R dash v1: SETTINGS and PIN MAP. Start here.
//  Board: Waveshare ESP32-S3-Touch-LCD-3.5 + 8-ch opto MOSFET board + GPS
//  + Waveshare MCP23017 board in the left controller.
// =====================================================================
#pragma once

// ---- Demo or real -----------------------------------------------------
// 0 = REAL: buttons, outputs, GPS speed, RPM input, brake input.
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

// ---- I2C bus (Waveshare fixed: SDA 8, SCL 7). The left controller hangs off it too.
#define I2C_HZ 100000            // 100 kHz for the ~1 m cable to the left controller

// ---- Left controller: MCP23017, buttons pull its pins to earth -----------
// The firmware searches 0x21-0x27 for it (0x20 is taken by the screen board's own chip).
// Which MCP pin (PA0..PA7) each button is on. Swap numbers here if a button does the wrong job.
#define BTN_IND_L  0   // PA0
#define BTN_IND_R  1   // PA1
#define BTN_HORN   2   // PA2
#define BTN_LIGHTS 3   // PA3
#define BTN_MODE   4   // PA4
static const uint32_t HOLD_MS     = 700;   // long press
static const uint32_t DEBOUNCE_MS = 25;
static const uint32_t PASS_FLASH_MS = 400;  // MODE tap: how long the high beam flashes
static const uint32_t LIGHTS_OFF_MS = 3000; // LIGHTS hold this long: headlight on (low) / off
static const uint32_t TRIP_RESET_MS = 3000; // MODE hold this long on the TRIP page: reset trip A

// ---- Outputs: GPIO -> MOSFET board IN1..IN8 (jumpers on H: HIGH = on) ----
//                               OUT1 OUT2 OUT3 OUT4 OUT5 OUT6 OUT7 OUT8
static const int PIN_OUT[8]  = {  38,  39,  40,  41,  42,  45,  46,  47 };
static const bool OUT_ACTIVE_HIGH = true;
enum OutIdx { O_IND_L = 0, O_IND_R, O_LOW, O_HIGH, O_HORN, O_USB, O_AUX, O_TAIL };
static const char *OUT_NAME[8] = {"IND L", "IND R", "LOW", "HIGH", "HORN", "USB", "DRL", "TAIL"};
static const bool LOW_WITH_HIGH   = true;    // keep low beam on with high (twin lamps)
static const uint32_t FLASH_PERIOD_MS = 667; // ~1.5 Hz indicators
static const int   TAIL_PWM_HZ = 1000;       // guess; slow MOSFET boards may want 200-500
static const float DRL_DIM_DUTY = 0.20f;     // DRL brightness while the headlight is on (sidelight). Full when it's off
static const float TAIL_DUTY   = 0.20f;      // tail brightness 0..1 (guess). Keep < 0.6 for brake sensing

// ---- Inputs ---------------------------------------------------------------
static const int PIN_RPM   = 21;   // HT-lead pickup, through its filter
static const int PIN_BRAKE = 48;   // opto across the rear lamp: LOW = brake on
static const float SPARKS_PER_REV   = 1.0f;   // guess: single-cylinder CDI fires every rev
static const uint32_t RPM_LOCKOUT_US = 3000;  // ignore pulses closer than this
static const uint32_t RPM_TIMEOUT_MS = 500;   // no pulse this long = engine stopped

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
