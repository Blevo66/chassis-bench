#pragma once
// =====================================================================
//  XL125R body-loom box: settings and PIN MAP
//  Hardware: Waveshare ESP32-S3-Touch-LCD-3.5 + Fowecry 8-ch opto MOSFET
//  board (3.3 V version, jumpers set to H) + UART GPS + MCP23017 for buttons.
//  Loom page: https://claude.ai/artifact/7RfLhucct5pzpFFF62vzXr
//
//  All loom pins are on the Waveshare's 2x16 header (J8). With no camera
//  fitted these are free: 17 18 21 38 39 40 41 42 45 46 47 48.
//  The screen, touch, SD card, audio and I2C (SDA 8 / SCL 7) are fixed by
//  the Waveshare board and are set in platformio.ini / below.
//
//  45 and 46 are strapping pins. They must be LOW at power-up, which the
//  MOSFET board's opto inputs (LED to earth) do for us, so they are used
//  for outputs, never for inputs with pull-ups.
// =====================================================================

// ---- Outputs: GPIO wired to IN1..IN8 on the MOSFET board -------------
//                         OUT1 OUT2 OUT3 OUT4 OUT5 OUT6 OUT7 OUT8
static const int PIN_OUT[8] = { 38,  39,  40,  41,  42,  45,  46,  47 };
static const bool OUT_ACTIVE_HIGH = true;   // jumpers on H: HIGH = MOSFET on

// What each output does (index = OUT number - 1)
enum OutIdx { O_IND_L = 0, O_IND_R, O_LOW, O_HIGH, O_HORN, O_USB, O_AUX, O_TAIL };

// ---- Rear light: ONE LED lamp, dim = tail, full = brake ----------------
// Lamp + to its fused feed, lamp - to OUT8. OUT8 PWMs it dim as a tail light.
// The brake switches are wired from lamp - to EARTH, in parallel with OUT8,
// so pressing the brake lights it full even if the ESP32 is dead (fail-safe).
static const int   TAIL_LEDC_CH  = 1;       // channel 0 is the screen backlight
static const int   TAIL_PWM_HZ   = 1000;    // guess: slow MOS-board drivers may need lower (try 200-500)
static const float TAIL_DUTY     = 0.20f;   // tail brightness, 0..1 (guess: 15-30% looks right). Keep < 0.6 so brake sensing works

// ---- Left controller: 5 buttons on an MCP23017 (I2C), each pulls to earth ----
// Set the MCP23017's A0, A1, A2 all HIGH (address 0x27). Its default 0x20
// clashes with the Waveshare's own TCA9554 expander.
static const uint8_t MCP_ADDR = 0x27;
// The MCP lives IN the left controller: 4 wires (3V3, GND, SDA, SCL) via
// AMPSEAL pins 16-19. Slow the bus to 100 kHz for the ~1 m cable.
static const uint32_t I2C_HZ = 100000;
//   MCP pin:                     GPA0 GPA1 GPA2 GPA3 GPA4
enum BtnIdx { B_IND_L = 0, B_IND_R, B_HORN, B_LIGHTS, B_MODE };
// Bench testing without the MCP23017: tap the screen to change page, and use
// the output buttons on the XL-DASH Wi-Fi page.

// ---- Other inputs -----------------------------------------------------
static const int PIN_RPM    = 21;  // HT-lead pickup, through the filter
static const int PIN_BRAKE  = 48;  // opto across the rear lamp: LOW while lamp - is at earth (internal pull-up on)
// No bike-volts pin: the header has no free ADC1 pin. The AXP2101 tells us when
// the 5 V feed drops (dash runs on its LiPo), and that is when the odo is saved.

// ---- GPS (UART2) and screen -------------------------------------------
static const int PIN_GPS_RX = 17;  // ESP32 receives here  <- GPS TX
static const int PIN_GPS_TX = 18;  // optional             -> GPS RX
static const uint32_t GPS_BAUD = 9600;   // most modules ship at 9600; set to yours
static const int PIN_TFT_BL = 6;   // Waveshare backlight (fixed)
static const int PIN_SDA = 8, PIN_SCL = 7;  // Waveshare I2C (fixed): AXP2101 0x34, touch 0x38, TCA9554 0x20
static const uint8_t TCA_ADDR = 0x20, TCA_LCD_RST_BIT = 1;   // screen reset is on expander pin 1
static const uint8_t AXP_ADDR = 0x34, TOUCH_ADDR = 0x38;
// Power: no on/off switch. Dash wakes when the bike's 5 V feed appears (engine running) and
// switches itself off this long after it goes (long enough to ride out a stall and re-kick).
static const uint32_t OFF_DELAY_S = 60;

// ---- Tunables (all guesses until tested on the bike) -----------------
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
// Electrex CD7003-DC: 9-16 V (manual). 4S Li-ion charges to 16.8 V, so it is OUT.
// Fits: 3S Li-ion (12.6 V full) or 4S LiFePO4 (14.6 V full).
static const bool     IGN_LIFEPO4        = false;   // true for LiFePO4 cells
static const int      IGN_CELLS          = 3;       // cells in series
static const float    IGN_CAPACITY_MAH   = 4000;    // pack capacity
static const float    IGN_ASSUMED_MA     = 700;     // used if no INA226: measure at fast idle
static const float    IGN_WARN_PER_CELL  = IGN_LIFEPO4 ? 3.20f : 3.55f;  // amber below this (V/cell)
static const float    IGN_LOW_PER_CELL   = IGN_LIFEPO4 ? 3.05f : 3.35f;  // red + "IGN BATT LOW" below this
static const uint32_t IGN_STALE_MS       = 20000;   // no advert for this long -> "IGN --"

