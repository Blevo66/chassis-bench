#pragma once
// =====================================================================
//  XL125R body-loom box: settings and PIN MAP
//  Matches loom page: https://claude.ai/artifact/7RfLhucct5pzpFFF62vzXr
//
//  !!! PROVISIONAL !!!  The 8 MOSFET pins below are PLACEHOLDERS.
//  The MOS board's PCB fixes which GPIO drives each OUT terminal.
//  Read them off the board (or seller's pin map) and fix PIN_OUT
//  before connecting anything. Every other pin must avoid those 8.
// =====================================================================

// ---- Outputs: OUT1..OUT8 on the MOS board (placeholders!) ----------
//                         OUT1 OUT2 OUT3 OUT4 OUT5 OUT6 OUT7 OUT8
static const int PIN_OUT[8] = { 26,  27,  19,   2,  15,  12,   0,  -1 };
static const bool OUT_ACTIVE_HIGH = true;   // guess: HIGH = MOSFET on

// What each output does (index = OUT number - 1)
enum OutIdx { O_IND_L = 0, O_IND_R, O_LOW, O_HIGH, O_HORN, O_USB, O_AUX, O_SPARE };

// ---- Left controller, 5 buttons, each pulls to earth when pressed ---
static const int PIN_BTN_IND_L  = 21;
static const int PIN_BTN_IND_R  = 22;
static const int PIN_BTN_HORN   = 13;
static const int PIN_BTN_LIGHTS = 14;
static const int PIN_BTN_MODE   = 25;
// 26/27 were the spare trip +/- pins; they are borrowed as OUT placeholders above.

// ---- Other inputs -----------------------------------------------------
static const int PIN_RPM    = 34;  // HT-lead pickup, through the filter (input-only pin)
static const int PIN_BRAKE  = 35;  // opto output, LOW when brake lamp is lit
static const int PIN_VOLTS  = 33;  // 100k / 22k divider from box supply (ADC1, works with WiFi)

// ---- GPS (UART2) and screen -------------------------------------------
static const int PIN_GPS_RX = 16;  // ESP32 receives here  <- GPS TX
static const int PIN_GPS_TX = 17;  // optional             -> GPS RX
static const uint32_t GPS_BAUD = 9600;   // u-blox default; raise after setting 10 Hz
static const int PIN_TFT_BL = 32;  // backlight PWM (screen SPI pins are in platformio.ini)

// ---- Tunables (all guesses until tested on the bike) -----------------
static const float  VOLT_DIVIDER     = (100.0f + 22.0f) / 22.0f;
static const float  VOLT_SAVE_BELOW  = 9.0f;    // save odo when supply starts to die
static const uint32_t HOLD_MS        = 700;     // long-press time
static const uint32_t DEBOUNCE_MS    = 25;
static const uint32_t FLASH_PERIOD_MS = 667;    // ~1.5 Hz indicators
static const float  SPARKS_PER_REV   = 1.0f;    // guess: single-cyl CDI fires every rev
static const uint32_t RPM_LOCKOUT_US = 3000;    // ignore pulses closer than this (20k rpm)
static const uint32_t RPM_TIMEOUT_MS = 500;     // no pulse for this long = engine stopped
static const int    SHIFT_RPM        = 9500;
static const int    RPM_MAX          = 11000;
static const bool   LOW_WITH_HIGH    = true;    // keep low beam on with high (twin lamps)
static const float  AUTO_CANCEL_MI   = 0.0f;    // indicator auto-cancel distance, 0 = off
static const float  GEAR_RPM_PER_MPH[6] = {0, 450, 300, 225, 180, 150}; // placeholder gearing

// ---- WiFi setup hotspot -------------------------------------------------
static const char*  AP_SSID     = "XL-DASH";
static const char*  AP_PASS     = "changeme123";   // change before use (8+ chars)
static const uint32_t AP_TIMEOUT_MS = 10UL * 60UL * 1000UL;  // hotspot off after 10 min
static const float  AP_OFF_ABOVE_MPH = 5.0f;                 // ...or once moving

// ---- Ignition battery (wireless sender, firmware/ign-sender) ----
// The engine loom is separate; the sender broadcasts its pack voltage (and
// current if it has an INA226) over Bluetooth. Values below are GUESSES:
// set them for your actual pack.
// CDI max is 16 V (Joel). 4S Li-ion charges to 16.8 V, so it is OUT.
// Fits: 3S Li-ion (12.6 V full) or 4S LiFePO4 (14.6 V full).
static const bool     IGN_LIFEPO4        = false;   // true for LiFePO4 cells
static const int      IGN_CELLS          = 3;       // cells in series
static const float    IGN_CAPACITY_MAH   = 4000;    // pack capacity
static const float    IGN_ASSUMED_MA     = 700;     // used if no INA226: measure at fast idle
static const float    IGN_WARN_PER_CELL  = IGN_LIFEPO4 ? 3.20f : 3.55f;  // amber below this (V/cell)
static const float    IGN_LOW_PER_CELL   = IGN_LIFEPO4 ? 3.05f : 3.35f;  // red + "IGN BATT LOW" below this
static const uint32_t IGN_STALE_MS       = 20000;   // no advert for this long -> "IGN --"

