// =====================================================================
//  XL brain box: SETTINGS and PIN MAP. Start here.
//  Board: ESP32-S3-DevKitC-1 (any ESP32-S3 dev board with these pins free)
//  + 8-ch opto MOSFET board + left controller (MCP23017) + RPM pickup + brake opto.
//  Everything bike-specific is in the "BIKE" section so the box can move bikes.
// =====================================================================
#pragma once

// ---- Pins on the ESP32-S3 board (my picks: avoid 0/3/45/46 strapping, 19/20 USB,
//      35-37 PSRAM, 43/44 USB-serial). Change here if your wiring differs.
//                               OUT1 OUT2 OUT3 OUT4 OUT5 OUT6 OUT7 OUT8
static const int PIN_OUT[8]  = {   4,   5,   6,   7,  15,  16,  17,  18 };
#define PIN_SDA 8              // left controller I2C
#define PIN_SCL 9
static const int PIN_RPM   = 10;   // HT-lead coil pickup, through its filter
static const int PIN_BRAKE = 11;   // opto across the rear lamp: LOW = brake on
#define LINK_TX_PIN 12         // to screen IO21 (screen's RX)
#define LINK_RX_PIN 13         // from screen IO48 (screen's TX)
#define LINK_BAUD 115200
#ifndef LINK_SERIAL
#define LINK_SERIAL Serial1
#endif

// ---- Outputs ------------------------------------------------------------------
static const bool OUT_ACTIVE_HIGH = true;    // MOSFET board jumpers on H
enum OutIdx { O_IND_L = 0, O_IND_R, O_LOW, O_HIGH, O_HORN, O_USB, O_DRL, O_TAIL };
static const char *OUT_NAME[8] = {"IND L", "IND R", "LOW", "HIGH", "HORN", "USB", "DRL", "TAIL"};
static const bool LOW_WITH_HIGH   = true;    // keep low beam on with high (twin lamps)
static const uint32_t FLASH_PERIOD_MS = 667; // ~1.5 Hz indicators
static const int   PWM_HZ = 1000;            // tail + DRL dimming (guess; slow MOSFET boards may want 200-500)
static const float TAIL_DUTY    = 0.20f;     // tail brightness 0..1. Keep < 0.6 for brake sensing
static const float DRL_DIM_DUTY = 0.20f;     // DRL while the headlight is on. Full when it's off

// ---- Left controller (MCP23017, searched for at 0x20-0x27) ------------------------
#define I2C_HZ 100000
#define BTN_IND_L  0   // PA0
#define BTN_IND_R  1   // PA1
#define BTN_HORN   2   // PA2
#define BTN_LIGHTS 3   // PA3
#define BTN_MODE   4   // PA4
static const uint32_t HOLD_MS       = 700;   // long press
static const uint32_t DEBOUNCE_MS   = 25;
static const uint32_t PASS_FLASH_MS = 400;   // MODE tap: high beam flash length
static const uint32_t LIGHTS_OFF_MS = 3000;  // LIGHTS hold: headlight on (low) / off
static const uint32_t TRIP_RESET_MS = 3000;  // MODE hold on the TRIP page: reset trip A

// ---- BIKE: change these when the box moves to another bike ---------------------
static const float SPARKS_PER_REV   = 1.0f;   // guess for the XL's DC-CDI single. If RPM reads double, 2.0
static const uint32_t RPM_LOCKOUT_US = 3000;  // ignore pulses closer than this (max ~20,000 rpm at 1/rev)
static const uint32_t RPM_TIMEOUT_MS = 500;   // no pulse this long = engine stopped
