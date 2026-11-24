// =====================================================================
//  XL125R body-loom box + dash
//  Waveshare ESP32-S3-Touch-LCD-3.5 + Fowecry 8-ch opto MOSFET board + UART GPS
//  v0.2, untested on hardware. Pin map: see config.h.
//
//  What it does:
//   - 5-button left controller: tap / long-press (see handleButtons)
//   - drives 8 MOSFET outputs: indicators flash in code, no flasher relay
//   - RPM from an HT-lead pickup, speed + clock from GPS
//   - 480x320 dash: Ride / Trip / System screens
//   - odometer + trips saved to flash, also when the supply starts to die
//   - WiFi hotspot "XL-DASH": live status, output test, firmware update
//   - ignition battery over Bluetooth (no wire to the engine loom): volts, %, time left
//  Rear light: one LED, PWM dim as tail on OUT8; brake switches short it to earth
//  in parallel, so the brake light works even with the ESP32 dead.
// =====================================================================
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Update.h>
#include <TFT_eSPI.h>
#include <TinyGPSPlus.h>
#include <NimBLEDevice.h>
#include "config.h"

// ------------------------------------------------------------------ state
struct State {
  bool indL = false, indR = false, hazard = false;
  bool high = false, flash = false, horn = false, aux = false, usb = true;
  bool brake = false;
  int  screen = 0;               // 0 ride, 1 trip, 2 system
  float rpm = 0, mph = 0;
  bool supplyOn = true;          // 5 V feed present (AXP2101 VBUS)
  float dashBattV = 0; int dashBattPct = -1; bool charging = false;
  bool gpsOk = false;
  int  sats = 0, gear = 0;
  double odo = 0, tripA = 0, tripB = 0, topMph = 0;
  double rideSecs = 0, rideMiles = 0;
  double indStartOdo = 0;        // for auto-cancel
  bool  outTest[8] = {};         // forced on from the web page
  bool  outState[8] = {};
} S;

TFT_eSPI tft;
TFT_eSprite spr(&tft);
TinyGPSPlus gps;
HardwareSerial GPSSerial(2);
Preferences prefs;
WebServer web(80);
bool apOn = false;
uint32_t apStartMs = 0;

// ------------------------------------------------------------------ RPM
volatile uint32_t rpmLastUs = 0, rpmPeriodUs = 0;
void IRAM_ATTR rpmISR() {
  uint32_t now = micros();
  uint32_t dt = now - rpmLastUs;
  if (dt < RPM_LOCKOUT_US) return;          // same spark ringing: ignore
  rpmPeriodUs = dt;
  rpmLastUs = now;
}
void updateRpm() {
  noInterrupts();
  uint32_t period = rpmPeriodUs, last = rpmLastUs;
  interrupts();
  float target = 0;
  if (period > 0 && (micros() - last) < RPM_TIMEOUT_MS * 1000UL)
    target = 60.0e6f / (period * SPARKS_PER_REV);
  S.rpm += (target - S.rpm) * 0.3f;         // light smoothing
  if (S.rpm < 50) S.rpm = 0;
}

// ------------------------------------------------------------------ I2C helpers
bool i2cWrite(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
int i2cRead(uint8_t addr, uint8_t reg) {          // -1 if the chip didn't answer
  Wire.beginTransmission(addr); Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(addr, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

// Screen reset is on pin 1 of the Waveshare's TCA9554 expander (as in Waveshare's example).
void lcdReset() {
  int out = i2cRead(TCA_ADDR, 0x01), cfg = i2cRead(TCA_ADDR, 0x03);
  if (out < 0 || cfg < 0) { Serial.println("TCA9554 not found"); return; }
  uint8_t bit = 1 << TCA_LCD_RST_BIT;
  i2cWrite(TCA_ADDR, 0x03, cfg & ~bit);           // that pin = output, others untouched
  i2cWrite(TCA_ADDR, 0x01, out | bit);  delay(10);
  i2cWrite(TCA_ADDR, 0x01, out & ~bit); delay(10);
  i2cWrite(TCA_ADDR, 0x01, out | bit);  delay(200);
}

// MCP23017 for the left-bar buttons (GPA0..4, pull-ups on, pressed = LOW)
bool mcpOk = false;
uint8_t btnMask = 0;                               // bit set = pressed
void mcpInit() {
  mcpOk = i2cWrite(MCP_ADDR, 0x00, 0xFF) && i2cWrite(MCP_ADDR, 0x0C, 0xFF);  // IODIRA all in, GPPUA pull-ups
  Serial.println(mcpOk ? "MCP23017 ok" : "MCP23017 not found: buttons off (bench mode)");
}
// The MCP sits in the left controller at the end of a cable through the plug,
// so it can be unplugged or drop out: on any read failure release all buttons
// and retry the init every 2 s.
void mcpRead() {
  static uint32_t lastTry = 0;
  if (!mcpOk) {
    btnMask = 0;
    if (millis() - lastTry > 2000) { lastTry = millis(); mcpInit(); }
    return;
  }
  int v = i2cRead(MCP_ADDR, 0x12);                 // GPIOA
  if (v < 0) { mcpOk = false; btnMask = 0; lastTry = millis(); return; }
  btnMask = (uint8_t)~v;
}

// AXP2101 power chip (register map from XPowersLib, not yet checked on the board)
void axpInit() {
  int adc = i2cRead(AXP_ADDR, 0x30);
  if (adc >= 0) i2cWrite(AXP_ADDR, 0x30, adc | 0x01);   // enable battery-voltage ADC
}
void axpRead() {
  int st1 = i2cRead(AXP_ADDR, 0x00), st2 = i2cRead(AXP_ADDR, 0x01);
  if (st1 < 0) return;                               // keep last values
  S.supplyOn = st1 & 0x20;                           // VBUS good
  bool battIn = st1 & 0x08;
  S.charging = st2 >= 0 && ((st2 >> 5) & 0x03) == 0x01;
  int h = i2cRead(AXP_ADDR, 0x34), l = i2cRead(AXP_ADDR, 0x35);
  S.dashBattV = (battIn && h >= 0 && l >= 0) ? (((h & 0x1F) << 8) | l) / 1000.0f : 0;
  int pct = i2cRead(AXP_ADDR, 0xA4);
  S.dashBattPct = (battIn && pct >= 0 && pct <= 100) ? pct : -1;
}

// FT6336 touch: a tap anywhere = next page (handy on the bench)
bool touchWasDown = false;
bool touchTapped() {
  int n = i2cRead(TOUCH_ADDR, 0x02);
  bool down = n > 0 && (n & 0x0F) > 0 && (n & 0x0F) < 3;
  bool tap = down && !touchWasDown;
  touchWasDown = down;
  return tap;
}

// ------------------------------------------------------------------ buttons
struct Button {
  int idx; bool down = false, held = false, lastRaw = false;
  uint32_t changedMs = 0, downMs = 0;
};
Button bL{B_IND_L}, bR{B_IND_R}, bHorn{B_HORN}, bLights{B_LIGHTS}, bMode{B_MODE};
Button* buttons[] = {&bL, &bR, &bHorn, &bLights, &bMode};

// returns: 0 nothing, 1 tap (on release), 2 hold started
int pollButton(Button& b) {
  bool raw = btnMask & (1 << b.idx);        // pressed pulls to earth
  uint32_t now = millis();
  if (raw != b.lastRaw) { b.lastRaw = raw; b.changedMs = now; }
  if (now - b.changedMs < DEBOUNCE_MS) return 0;
  if (raw && !b.down) { b.down = true; b.held = false; b.downMs = now; }
  if (raw && b.down && !b.held && now - b.downMs >= HOLD_MS) { b.held = true; return 2; }
  if (!raw && b.down) { b.down = false; if (!b.held) return 1; }
  return 0;
}

void saveTrips();
void handleButtons() {
  int e;
  mcpRead();
  if (touchTapped()) S.screen = (S.screen + 1) % 3;
  // Indicators: tap = on/cancel (cancels the other side), hold = hazards
  if ((e = pollButton(bL))) {
    if (e == 1) { S.hazard = false; S.indR = false; S.indL = !S.indL; S.indStartOdo = S.odo; }
    else        { S.hazard = !S.hazard; S.indL = S.indR = false; }
  }
  if ((e = pollButton(bR))) {
    if (e == 1) { S.hazard = false; S.indL = false; S.indR = !S.indR; S.indStartOdo = S.odo; }
    else        { S.hazard = !S.hazard; S.indL = S.indR = false; }
  }
  // Horn: on exactly while pressed (no debounce delay on press for safety)
  pollButton(bHorn);
  S.horn = btnMask & (1 << B_HORN);
  // Lights: tap = high/low, hold = flash high beam while held
  if ((e = pollButton(bLights)) == 1) S.high = !S.high;
  S.flash = bLights.down && bLights.held;
  // Mode: tap = next screen, hold = reset trip A
  if ((e = pollButton(bMode))) {
    if (e == 1) S.screen = (S.screen + 1) % 3;
    else { S.tripA = 0; S.topMph = 0; S.rideSecs = 0; S.rideMiles = 0; saveTrips(); }
  }
  // Optional auto-cancel
  if (AUTO_CANCEL_MI > 0 && (S.indL || S.indR) && S.odo - S.indStartOdo > AUTO_CANCEL_MI)
    S.indL = S.indR = false;
}

// ------------------------------------------------------------------ outputs
bool flashPhase() { return (millis() % FLASH_PERIOD_MS) < FLASH_PERIOD_MS / 2; }

void writeOutputs() {
  bool f = flashPhase();
  bool want[8];
  want[O_IND_L] = (S.indL || S.hazard) && f;
  want[O_IND_R] = (S.indR || S.hazard) && f;
  bool highOn   = S.high || S.flash;
  want[O_HIGH]  = highOn;
  want[O_LOW]   = !highOn || LOW_WITH_HIGH;   // low beam on from boot
  want[O_HORN]  = S.horn;
  want[O_USB]   = S.usb;
  want[O_AUX]   = S.aux;
  want[O_TAIL]  = true;                       // tail dim always on; brake = hardware, full
  for (int i = 0; i < 8; i++) {
    bool on = want[i] || S.outTest[i];
    S.outState[i] = on;
    if (PIN_OUT[i] < 0) continue;
    if (i == O_TAIL) {
      float d = S.outTest[i] ? 1.0f : (on ? TAIL_DUTY : 0.0f);
      if (!OUT_ACTIVE_HIGH) d = 1.0f - d;
      ledcWrite(TAIL_LEDC_CH, (uint32_t)(d * 255.0f + 0.5f));
    } else {
      digitalWrite(PIN_OUT[i], on == OUT_ACTIVE_HIGH ? HIGH : LOW);
    }
  }
}

// ------------------------------------------------------------------ GPS, volts, odo
uint32_t lastOdoMs = 0;
double lastSavedOdo = 0;
bool savedOnLowVolts = false;

void saveTrips() {
  prefs.putDouble("odo", S.odo);
  prefs.putDouble("tripA", S.tripA);
  prefs.putDouble("tripB", S.tripB);
  lastSavedOdo = S.odo;
}

void updateGpsAndOdo() {
  while (GPSSerial.available()) gps.encode(GPSSerial.read());
  S.sats  = gps.satellites.isValid() ? gps.satellites.value() : 0;
  S.gpsOk = gps.location.isValid() && gps.location.age() < 2000 && S.sats >= 4;
  float mph = (S.gpsOk && gps.speed.isValid()) ? gps.speed.mph() : 0;
  S.mph = mph < 1.5f ? 0 : mph;              // kill GPS jitter at standstill

  uint32_t now = millis();
  float dt = (now - lastOdoMs) / 1000.0f;
  lastOdoMs = now;
  if (S.gpsOk && S.mph > 2.0f) {
    double mi = S.mph * dt / 3600.0;
    S.odo += mi; S.tripA += mi; S.tripB += mi;
    S.rideMiles += mi; S.rideSecs += dt;
    if (S.mph > S.topMph) S.topMph = S.mph;
  }
  if (S.odo - lastSavedOdo >= 0.1) saveTrips();   // every 0.1 mile

  // gear: nearest ratio within 15%
  S.gear = 0;
  if (S.mph > 3 && S.rpm > 1000) {
    float r = S.rpm / S.mph, best = 1e9;
    for (int g = 1; g <= 5; g++) {
      float err = fabsf(r - GEAR_RPM_PER_MPH[g]) / GEAR_RPM_PER_MPH[g];
      if (err < 0.15f && err < best) { best = err; S.gear = g; }
    }
  }
}

void updatePower() {
  axpRead();
  // bike supply gone (no battery on the body loom): the dash is now on its LiPo, save once
  static uint32_t lostMs = 0;
  if (!S.supplyOn && !savedOnLowVolts) { saveTrips(); savedOnLowVolts = true; lostMs = millis(); }
  if (S.supplyOn) savedOnLowVolts = false;
  // Auto-off: bike supply gone for OFF_DELAY_S (engine stopped, not just a stall) -> switch
  // the whole board off through the AXP2101 so the LiPo isn't drained. It comes back on when
  // the bike supply returns (AXP powers up on VBUS) or from a press on PWRON.
  static bool offTried = false;
  if (S.supplyOn) offTried = false;
  if (!S.supplyOn && !apOn && !offTried && millis() - lostMs > OFF_DELAY_S * 1000UL) {
    offTried = true;                                  // once only: no flash-wear loop if the write fails
    saveTrips();
    int r = i2cRead(AXP_ADDR, 0x10);                 // PMU common config, bit0 = soft power-off (XPowersLib shutdown(); check on the bench)
    if (r >= 0) i2cWrite(AXP_ADDR, 0x10, r | 0x01);
  }
}

// Brake sense: the opto sees lamp - at earth. The tail PWM pulls it to earth only
// TAIL_DUTY of the time; the brake switch holds it there. So: brake = LOW for a
// whole PWM period. 16 reads spread over ~1.3 periods.
void readBrake() {
  const uint32_t stepUs = (1300000UL / TAIL_PWM_HZ) / 16;
  for (int i = 0; i < 16; i++) {
    if (digitalRead(PIN_BRAKE) != LOW) { S.brake = false; return; }
    delayMicroseconds(stepUs);
  }
  S.brake = true;
}

// ------------------------------------------------------------------ ignition battery (BLE)
// Payload from firmware/ign-sender: FF FF 'X' 'L' mV(2) mA(2) seq
volatile uint16_t ignRxMv = 0, ignRxMa = 0xFFFF;
volatile uint32_t ignRxMs = 0;
struct { bool ok = false; float volts = 0, pct = 0, ma = 0, hoursLeft = 0; bool sensed = false; } IGN;

class IgnScanCB : public NimBLEAdvertisedDeviceCallbacks {
  void onResult(NimBLEAdvertisedDevice* d) override {
    if (!d->haveManufacturerData()) return;
    std::string m = d->getManufacturerData();
    if (m.size() < 9 || (uint8_t)m[0] != 0xFF || (uint8_t)m[1] != 0xFF || m[2] != 'X' || m[3] != 'L') return;
    ignRxMv = (uint8_t)m[4] | ((uint8_t)m[5] << 8);
    ignRxMa = (uint8_t)m[6] | ((uint8_t)m[7] << 8);
    ignRxMs = millis();
  }
};

void startIgnScan() {
  NimBLEDevice::init("");
  NimBLEScan* sc = NimBLEDevice::getScan();
  sc->setAdvertisedDeviceCallbacks(new IgnScanCB(), true);  // want every advert, not just new devices
  sc->setActiveScan(false);
  sc->setInterval(160); sc->setWindow(60);                  // 100 ms / 37.5 ms: leaves air time for WiFi
  sc->setMaxResults(0);                                     // don't store results, just call back
  sc->start(0, nullptr, false);                             // scan forever
}

// Rough state of charge from volts per cell (typical curves, GUESSES for your cells)
float cellPct(float vCell) {
  static const float VL[] = {3.00f, 3.30f, 3.40f, 3.50f, 3.60f, 3.70f, 3.80f, 3.90f, 4.00f, 4.10f, 4.20f};  // Li-ion
  static const float VF[] = {2.80f, 3.00f, 3.10f, 3.20f, 3.23f, 3.26f, 3.28f, 3.30f, 3.32f, 3.35f, 3.45f};  // LiFePO4 (flat!)
  static const float P[]  = {0,     4,     8,     15,    28,    42,    55,    68,    80,    90,    100};
  const float* V = IGN_LIFEPO4 ? VF : VL;
  if (vCell <= V[0]) return 0; if (vCell >= V[10]) return 100;
  for (int i = 0; i < 10; i++) if (vCell < V[i + 1]) return P[i] + (P[i + 1] - P[i]) * (vCell - V[i]) / (V[i + 1] - V[i]);
  return 100;
}

void updateIgn() {
  uint32_t rx = ignRxMs;
  IGN.ok = rx && millis() - rx < IGN_STALE_MS;
  if (!IGN.ok) return;
  float v = ignRxMv / 1000.0f;
  IGN.volts += (v - IGN.volts) * (IGN.volts == 0 ? 1.0f : 0.3f);
  IGN.pct = cellPct(IGN.volts / IGN_CELLS);
  IGN.sensed = ignRxMa != 0xFFFF;
  float ma = IGN.sensed ? (float)ignRxMa : IGN_ASSUMED_MA;
  IGN.ma += (ma - IGN.ma) * (IGN.ma == 0 ? 1.0f : 0.02f);   // slow average: CDI current comes in pulses
  IGN.hoursLeft = IGN.ma > 1 ? (IGN.pct / 100.0f) * IGN_CAPACITY_MAH / IGN.ma : 0;
}

uint8_t ignColour();   // defined with the display code
String ignTimeLeft() {
  int mins = (int)(IGN.hoursLeft * 60);
  return String(mins / 60) + "h " + (mins % 60 < 10 ? "0" : "") + String(mins % 60) + "m";
}

// ------------------------------------------------------------------ display
// 3.5" ST7796 IPS, 480x320 landscape. The frame is a 4-bit sprite (75 KB) with a
// 16-colour palette: small enough for internal RAM, so pushing it stays fast. In a 4-bit sprite every
// colour below is a PALETTE INDEX, not an RGB565 value.
enum : uint8_t { P_BLACK = 0, P_WHITE, P_DIM, P_GREY, P_AMBER, P_RED, P_GREEN, P_BLUE };
uint16_t palette[16] = {
  TFT_BLACK, TFT_WHITE, 0x18E3 /*dim*/, 0x7BEF /*grey*/, 0xFD60 /*amber*/,
  0xF8A6 /*red*/, 0x2EED /*green*/, 0x3C5F /*blue*/,
  0, 0, 0, 0, 0, 0, 0, 0
};

uint8_t ignColour() {
  float vc = IGN.volts / IGN_CELLS;
  return !IGN.ok ? P_GREY : vc < IGN_LOW_PER_CELL ? P_RED : vc < IGN_WARN_PER_CELL ? P_AMBER : P_GREEN;
}

void arrow(int x, int y, int dir, bool on) {          // 40 x 28 px
  uint8_t c = on ? P_GREEN : P_DIM;
  if (dir < 0) { spr.fillTriangle(x, y, x + 22, y - 14, x + 22, y + 14, c); spr.fillRect(x + 22, y - 6, 18, 13, c); }
  else         { spr.fillTriangle(x + 40, y, x + 18, y - 14, x + 18, y + 14, c); spr.fillRect(x, y - 6, 18, 13, c); }
}

void drawTop() {
  bool f = flashPhase();
  arrow(10, 23, -1, (S.indL || S.hazard) && f);
  arrow(430, 23, 1, (S.indR || S.hazard) && f);
  uint8_t hb = (S.high || S.flash) ? P_BLUE : P_DIM;     // high-beam symbol
  spr.fillCircle(78, 23, 10, hb);
  for (int i = -1; i <= 1; i++) { spr.drawFastHLine(84, 23 + i * 7, 16, hb); spr.drawFastHLine(84, 24 + i * 7, 16, hb); }
  if (S.brake) { spr.fillRoundRect(112, 11, 46, 24, 4, P_RED); spr.setTextColor(P_BLACK); spr.drawCentreString("BRK", 135, 15, 2); }
  spr.setTextColor(P_WHITE);
  char buf[16];
  if (gps.time.isValid() && S.gpsOk) {
    // UTC from GPS; UK local time offset not handled yet (BST = +1)
    snprintf(buf, sizeof buf, "%02d:%02d", gps.time.hour(), gps.time.minute());
  } else strcpy(buf, "--:--");
  spr.drawCentreString(buf, 240, 10, 4);                 // font 4 = 26 px
  spr.setTextColor(S.gpsOk ? P_GREY : P_AMBER);
  snprintf(buf, sizeof buf, S.gpsOk ? "GPS %d" : "NO GPS", S.sats);
  spr.drawRightString(buf, 412, 15, 2);
  spr.drawFastHLine(0, 46, 480, P_DIM);
}

void drawRpmBar() {
  const int n = 30, bx = 14, by = 56, bw = 452, bh = 32, gap = 3;
  const int w = (bw - gap * (n - 1)) / n;
  int lit = (int)roundf(S.rpm / RPM_MAX * n);
  for (int i = 0; i < n; i++) {
    float r = (i + 1) * (float)RPM_MAX / n;
    int h = bh * (0.45f + 0.55f * i / (n - 1));
    uint8_t c = r > SHIFT_RPM ? P_RED : r > 7500 ? P_AMBER : P_WHITE;
    spr.fillRect(bx + i * (w + gap), by + bh - h, w, h, i < lit ? c : P_DIM);
  }
  spr.setTextColor(P_GREY);
  spr.drawString("x1000", 14, 94, 2);
  for (int k = 2; k <= 10; k += 2) spr.drawCentreString(String(k), bx + k * bw / 11, 94, 2);
  if (S.rpm > SHIFT_RPM && flashPhase()) {
    spr.fillRect(378, 92, 88, 20, P_RED); spr.setTextColor(P_WHITE); spr.drawCentreString("SHIFT", 422, 94, 2);
  }
}

void drawBottom(const String& a, const String& b) {
  spr.drawFastHLine(0, 274, 480, P_DIM);
  spr.setTextColor(P_WHITE);
  spr.drawString(a, 14, 284, 4);
  if (b.length()) spr.drawRightString(b, 466, 284, 4);
}

void drawRide() {
  drawRpmBar();
  spr.setTextColor(P_WHITE);
  spr.setTextSize(3);                          // font 7 (7-segment, 48 px) x3 = 144 px tall
  if (S.gpsOk) spr.drawRightString(String((int)roundf(S.mph)), 300, 122, 7);
  else         spr.drawRightString("--", 300, 122, 7);
  spr.setTextSize(1);
  spr.setTextColor(P_GREY); spr.drawString("MPH", 306, 240, 2);
  spr.drawRect(346, 124, 120, 90, P_GREY); spr.drawRect(347, 125, 118, 88, P_GREY);
  spr.drawCentreString("GEAR", 406, 132, 2);
  spr.setTextColor(P_WHITE);
  spr.drawCentreString(S.gear ? String(S.gear) : String("-"), 406, 152, 6);   // font 6 = 48 px digits
  spr.setTextColor(P_GREY);
  spr.drawCentreString(String((int)S.rpm) + " rpm", 406, 222, 2);
  spr.setTextColor(ignColour());
  spr.drawCentreString(IGN.ok ? "IGN " + String(IGN.volts, 1) + "V " + String((int)IGN.pct) + "%" : String("IGN --"), 406, 244, 2);
  drawBottom("ODO " + String(S.odo, 1), "TRIP A " + String(S.tripA, 1));
  if (!S.supplyOn) { spr.setTextColor(P_AMBER); spr.drawCentreString("ON LIPO", 240, 252, 2); }
}

String hms(double s) {
  long t = (long)s; char b[12];
  snprintf(b, sizeof b, "%ld:%02ld:%02ld", t / 3600, (t % 3600) / 60, t % 60);
  return b;
}

void drawTrip() {
  spr.setTextColor(P_AMBER); spr.drawString("TRIP", 14, 58, 4);
  const char* k[] = {"TRIP A", "TRIP B", "RIDE TIME", "AVG SPEED", "TOP SPEED"};
  String v[] = {String(S.tripA, 1) + " mi", String(S.tripB, 1) + " mi", hms(S.rideSecs),
                String(S.rideSecs > 0 ? S.rideMiles / (S.rideSecs / 3600.0) : 0, 1) + " mph",
                String(S.topMph, 0) + " mph"};
  for (int i = 0; i < 5; i++) {
    spr.setTextColor(P_GREY);  spr.drawString(k[i], 14, 96 + i * 34, 4);
    spr.setTextColor(P_WHITE); spr.drawRightString(v[i], 466, 96 + i * 34, 4);
  }
  drawBottom("Hold MODE: reset trip A", "");
}

void drawSystem() {
  spr.setTextColor(P_AMBER); spr.drawString("SYSTEM", 14, 58, 4);
  spr.setTextColor(P_GREY); spr.drawString("SUPPLY", 14, 96, 4);
  spr.setTextColor(S.supplyOn ? P_GREEN : P_AMBER);
  spr.drawRightString(S.supplyOn ? "on" : "LIPO", 236, 96, 4);
  spr.setTextColor(P_GREY);
  spr.drawString(S.dashBattPct >= 0 ? "dash lipo " + String(S.dashBattV, 2) + "V " + String(S.dashBattPct) + "%" + (S.charging ? " chg" : "")
                                    : String("dash lipo --"), 14, 116, 2);
  spr.setTextColor(P_GREY); spr.drawString("GPS", 14, 130, 4);
  spr.setTextColor(P_WHITE); spr.drawRightString(S.gpsOk ? String(S.sats) + " sats" : "no fix", 236, 130, 4);
  spr.setTextColor(P_GREY); spr.drawString("WIFI", 14, 164, 4);
  spr.setTextColor(P_WHITE); spr.drawRightString(apOn ? "on" : "off", 236, 164, 4);
  spr.setTextColor(P_GREY); spr.drawString("IGN", 14, 198, 4);
  spr.setTextColor(ignColour());
  spr.drawRightString(IGN.ok ? String(IGN.volts, 1) + " V" : String("no signal"), 236, 198, 4);
  if (IGN.ok) {
    spr.setTextColor(P_GREY);
    spr.drawString(String((int)IGN.pct) + "%  " + String((int)IGN.ma) + (IGN.sensed ? " mA" : " mA est") + "  ~" + ignTimeLeft(), 14, 232, 2);
  }
  const char* names[] = {"1 IND L", "2 IND R", "3 LOW", "4 HIGH", "5 HORN", "6 USB", "7 AUX", "8 TAIL/BRK"};
  for (int i = 0; i < 8; i++) {
    int y = 88 + i * 22;
    spr.fillRect(268, y + 1, 14, 14, S.outState[i] ? P_GREEN : P_DIM);
    spr.setTextColor(S.outState[i] ? P_WHITE : P_GREY);
    spr.drawString(names[i], 292, y, 2);
  }
  drawBottom("Outputs live", "");
}

void drawScreen() {
  spr.fillSprite(P_BLACK);
  drawTop();
  if (S.screen == 0) drawRide(); else if (S.screen == 1) drawTrip(); else drawSystem();
  if (IGN.ok && IGN.volts / IGN_CELLS < IGN_LOW_PER_CELL && flashPhase()) {
    spr.fillRect(120, 140, 240, 44, P_RED); spr.setTextColor(P_WHITE); spr.drawCentreString("IGN BATT LOW", 240, 149, 4);
  }
  if (S.horn) { spr.fillRect(180, 248, 120, 24, P_AMBER); spr.setTextColor(P_BLACK); spr.drawCentreString("HORN", 240, 252, 2); }
  spr.pushSprite(0, 0);
}

// ------------------------------------------------------------------ WiFi page
const char PAGE[] PROGMEM = R"HTML(<!doctype html><meta name=viewport content="width=device-width">
<title>XL dash</title><style>body{font-family:sans-serif;background:#111;color:#eee;margin:16px}
button{padding:10px 14px;margin:4px;border:0;border-radius:8px;background:#333;color:#fff}
.on{background:#2a7}</style><h2>XL125R box</h2><pre id=s></pre><h3>Test outputs</h3><div id=o></div>
<h3>Firmware update</h3><form method=POST action=/update enctype=multipart/form-data>
<input type=file name=f><button>Upload .bin</button></form>
<script>const n=['IND L','IND R','LOW','HIGH','HORN','USB','AUX','TAIL (full)'];
async function t(){const r=await fetch('/api/state');const j=await r.json();
document.getElementById('s').textContent=`RPM ${j.rpm}  MPH ${j.mph}  lipo ${j.volts} V\nGPS ${j.sats} sats ${j.gps?'fix':'no fix'}  ODO ${j.odo}`;
document.getElementById('o').innerHTML=n.map((x,i)=>`<button class="${j.out[i]?'on':''}" onclick="fetch('/api/test?n=${i}')">${i+1} ${x}</button>`).join('');}
setInterval(t,500);t();</script>)HTML";

void startAP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  web.on("/", [] { web.send_P(200, "text/html", PAGE); });
  web.on("/api/state", [] {
    String j = "{\"rpm\":" + String((int)S.rpm) + ",\"mph\":" + String(S.mph, 1) +
               ",\"volts\":" + String(S.dashBattV, 2) + ",\"sats\":" + String(S.sats) +
               ",\"gps\":" + String(S.gpsOk ? "true" : "false") + ",\"odo\":" + String(S.odo, 1) +
               ",\"ign\":" + String(IGN.ok ? IGN.volts : 0, 2) + ",\"ignPct\":" + String((int)IGN.pct) + ",\"out\":[";
    for (int i = 0; i < 8; i++) j += String(S.outState[i] ? 1 : 0) + (i < 7 ? "," : "");
    web.send(200, "application/json", j + "]}");
  });
  web.on("/api/test", [] {                      // toggle a forced-on output (bench testing)
    int n = web.arg("n").toInt();
    if (n >= 0 && n < 8) S.outTest[n] = !S.outTest[n];
    web.send(200, "text/plain", "ok");
  });
  web.on("/update", HTTP_POST,
    [] { web.send(200, "text/plain", Update.hasError() ? "FAILED" : "OK, rebooting"); delay(500); ESP.restart(); },
    [] {
      HTTPUpload& u = web.upload();
      if (u.status == UPLOAD_FILE_START) Update.begin(UPDATE_SIZE_UNKNOWN);
      else if (u.status == UPLOAD_FILE_WRITE) Update.write(u.buf, u.currentSize);
      else if (u.status == UPLOAD_FILE_END) Update.end(true);
    });
  web.begin();
  apOn = true; apStartMs = millis();
}

void stopAP() {
  web.stop(); WiFi.softAPdisconnect(true); WiFi.mode(WIFI_OFF);
  apOn = false;
  for (bool& t : S.outTest) t = false;
}

// ------------------------------------------------------------------ setup / loop
void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 8; i++) if (PIN_OUT[i] >= 0) { pinMode(PIN_OUT[i], OUTPUT); digitalWrite(PIN_OUT[i], OUT_ACTIVE_HIGH ? LOW : HIGH); }
  if (PIN_OUT[O_TAIL] >= 0) { ledcSetup(TAIL_LEDC_CH, TAIL_PWM_HZ, 8); ledcAttachPin(PIN_OUT[O_TAIL], TAIL_LEDC_CH); }
  Wire.begin(PIN_SDA, PIN_SCL, I2C_HZ);   // 100 kHz: the bus runs out to the left controller
  mcpInit();
  axpInit();
  pinMode(PIN_RPM, INPUT);                       // filter sets the level
  pinMode(PIN_BRAKE, INPUT_PULLUP);              // opto pulls it LOW
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), rpmISR, RISING);

  prefs.begin("xl", false);
  S.odo = prefs.getDouble("odo", 0); S.tripA = prefs.getDouble("tripA", 0); S.tripB = prefs.getDouble("tripB", 0);
  lastSavedOdo = S.odo;

  GPSSerial.begin(GPS_BAUD, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);

  lcdReset();
  tft.init(); tft.setRotation(1); tft.fillScreen(TFT_BLACK);
  ledcSetup(0, 5000, 8); ledcAttachPin(PIN_TFT_BL, 0); ledcWrite(0, 255);
  spr.setColorDepth(4);                          // 480x320 x 4 bit = 75 KB, fits without PSRAM
  if (!spr.createSprite(480, 320)) Serial.println("sprite alloc FAILED");
  spr.createPalette(palette, 16);

  writeOutputs();                                // low beam on straight away
  startAP();
  startIgnScan();                                // after the sprite and WiFi have their memory
}

uint32_t lastDraw = 0, lastSlow = 0;
void loop() {
  handleButtons();
  readBrake();
  updateRpm();
  writeOutputs();
  updateGpsAndOdo();
  if (millis() - lastSlow > 50) { lastSlow = millis(); updatePower(); updateIgn(); }
  if (millis() - lastDraw > 50) { lastDraw = millis(); drawScreen(); }   // ~20 fps
  if (apOn) {
    web.handleClient();
    if (millis() - apStartMs > AP_TIMEOUT_MS || S.mph > AP_OFF_ABOVE_MPH) stopAP();
  }
}
