// =====================================================================
//  XL125R body-loom box + dash  (ESP32 8-ch MOS board, 3.2" TFT, M10 GPS)
//  v0.1, untested on hardware. Pins are PROVISIONAL: see config.h.
//
//  What it does:
//   - 5-button left controller: tap / long-press (see handleButtons)
//   - drives 8 MOSFET outputs: indicators flash in code, no flasher relay
//   - RPM from an HT-lead pickup, speed + clock from GPS
//   - 320x240 dash: Ride / Trip / System screens
//   - odometer + trips saved to flash, also when the supply starts to die
//   - WiFi hotspot "XL-DASH": live status, output test, firmware update
//  The brake light is NOT switched here (hard-wired); we only sense it.
// =====================================================================
#include <Arduino.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Update.h>
#include <TFT_eSPI.h>
#include <TinyGPSPlus.h>
#include "config.h"

// ------------------------------------------------------------------ state
struct State {
  bool indL = false, indR = false, hazard = false;
  bool high = false, flash = false, horn = false, aux = false, usb = true;
  bool brake = false;
  int  screen = 0;               // 0 ride, 1 trip, 2 system
  float rpm = 0, mph = 0, volts = 0;
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

// ------------------------------------------------------------------ buttons
struct Button {
  int pin; bool down = false, held = false, lastRaw = false;
  uint32_t changedMs = 0, downMs = 0;
};
Button bL{PIN_BTN_IND_L}, bR{PIN_BTN_IND_R}, bHorn{PIN_BTN_HORN}, bLights{PIN_BTN_LIGHTS}, bMode{PIN_BTN_MODE};
Button* buttons[] = {&bL, &bR, &bHorn, &bLights, &bMode};

// returns: 0 nothing, 1 tap (on release), 2 hold started
int pollButton(Button& b) {
  bool raw = digitalRead(b.pin) == LOW;     // pressed pulls to earth
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
  S.horn = digitalRead(PIN_BTN_HORN) == LOW;
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
  want[O_SPARE] = false;
  for (int i = 0; i < 8; i++) {
    bool on = want[i] || S.outTest[i];
    S.outState[i] = on;
    if (PIN_OUT[i] >= 0) digitalWrite(PIN_OUT[i], on == OUT_ACTIVE_HIGH ? HIGH : LOW);
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

void updateVolts() {
  float v = analogReadMilliVolts(PIN_VOLTS) / 1000.0f * VOLT_DIVIDER;
  S.volts += (v - S.volts) * 0.2f;
  // supply dying (no battery on the body loom): save once
  if (S.volts < VOLT_SAVE_BELOW && S.volts > 2.0f && !savedOnLowVolts) { saveTrips(); savedOnLowVolts = true; }
  if (S.volts > VOLT_SAVE_BELOW + 1.0f) savedOnLowVolts = false;
  S.brake = digitalRead(PIN_BRAKE) == LOW;
}

// ------------------------------------------------------------------ display
const uint16_t COL_DIM = 0x18E3, COL_GREY = 0x7BEF, COL_AMBER = 0xFD60, COL_RED = 0xF8A6,
               COL_GREEN = 0x2EED, COL_BLUE = 0x3C5F;

void arrow(int x, int y, int dir, bool on) {
  uint16_t c = on ? COL_GREEN : COL_DIM;
  if (dir < 0) { spr.fillTriangle(x, y, x + 16, y - 10, x + 16, y + 10, c); spr.fillRect(x + 16, y - 4, 12, 9, c); }
  else         { spr.fillTriangle(x + 28, y, x + 12, y - 10, x + 12, y + 10, c); spr.fillRect(x, y - 4, 12, 9, c); }
}

void drawTop() {
  bool f = flashPhase();
  arrow(8, 16, -1, (S.indL || S.hazard) && f);
  arrow(284, 16, 1, (S.indR || S.hazard) && f);
  uint16_t hb = (S.high || S.flash) ? COL_BLUE : COL_DIM;
  spr.fillCircle(56, 16, 7, hb);
  for (int i = -1; i <= 1; i++) spr.drawFastHLine(60, 16 + i * 5, 11, hb);
  if (S.brake) { spr.fillRoundRect(80, 8, 30, 16, 3, COL_RED); spr.setTextColor(TFT_BLACK); spr.drawCentreString("BRK", 95, 9, 2); }
  spr.setTextColor(TFT_WHITE);
  char buf[16];
  if (gps.time.isValid() && S.gpsOk) {
    // UTC from GPS; UK local time offset not handled yet (BST = +1)
    snprintf(buf, sizeof buf, "%02d:%02d", gps.time.hour(), gps.time.minute());
  } else strcpy(buf, "--:--");
  spr.drawCentreString(buf, 160, 8, 2);
  spr.setTextColor(S.gpsOk ? COL_GREY : COL_AMBER);
  snprintf(buf, sizeof buf, S.gpsOk ? "GPS %d" : "NO GPS", S.sats);
  spr.drawRightString(buf, 270, 9, 2);
  spr.drawFastHLine(0, 32, 320, COL_DIM);
}

void drawRpmBar() {
  const int n = 24, bx = 10, by = 40, bw = 300, bh = 22, gap = 2;
  const int w = (bw - gap * (n - 1)) / n;
  int lit = (int)roundf(S.rpm / RPM_MAX * n);
  for (int i = 0; i < n; i++) {
    float r = (i + 1) * (float)RPM_MAX / n;
    int h = bh * (0.45f + 0.55f * i / (n - 1));
    uint16_t c = r > SHIFT_RPM ? COL_RED : r > 7500 ? COL_AMBER : TFT_WHITE;
    spr.fillRect(bx + i * (w + gap), by + bh - h, w, h, i < lit ? c : COL_DIM);
  }
  spr.setTextColor(COL_GREY);
  spr.drawString("x1000", 10, 66, 1);
  for (int k = 2; k <= 10; k += 2) spr.drawCentreString(String(k), bx + k * bw / 11, 66, 1);
  if (S.rpm > SHIFT_RPM && flashPhase()) {
    spr.fillRect(250, 64, 60, 13, COL_RED); spr.setTextColor(TFT_WHITE); spr.drawCentreString("SHIFT", 280, 67, 1);
  }
}

void drawBottom(const String& a, const String& b) {
  spr.drawFastHLine(0, 206, 320, COL_DIM);
  spr.setTextColor(TFT_WHITE);
  spr.drawString(a, 10, 214, 2);
  if (b.length()) spr.drawRightString(b, 310, 214, 2);
}

void drawRide() {
  drawRpmBar();
  spr.setTextColor(TFT_WHITE);
  spr.setTextSize(2);                          // font 7 (7-segment) x2 = 96 px
  if (S.gpsOk) spr.drawRightString(String((int)roundf(S.mph)), 205, 88, 7);
  else         spr.drawRightString("--", 205, 88, 7);
  spr.setTextSize(1);
  spr.setTextColor(COL_GREY); spr.drawString("MPH", 212, 170, 2);
  spr.drawRect(244, 92, 62, 56, COL_GREY);
  spr.drawCentreString("GEAR", 275, 96, 1);
  spr.setTextColor(TFT_WHITE);
  spr.drawCentreString(S.gear ? String(S.gear) : String("-"), 275, 108, 4);
  spr.setTextColor(COL_GREY);
  spr.drawCentreString(String((int)S.rpm) + " rpm", 275, 156, 2);
  drawBottom("ODO " + String(S.odo, 1), "TRIP A " + String(S.tripA, 1));
}

String hms(double s) {
  long t = (long)s; char b[12];
  snprintf(b, sizeof b, "%ld:%02ld:%02ld", t / 3600, (t % 3600) / 60, t % 60);
  return b;
}

void drawTrip() {
  spr.setTextColor(COL_AMBER); spr.drawString("TRIP", 10, 42, 2);
  const char* k[] = {"TRIP A", "TRIP B", "RIDE TIME", "AVG SPEED", "TOP SPEED"};
  String v[] = {String(S.tripA, 1) + " mi", String(S.tripB, 1) + " mi", hms(S.rideSecs),
                String(S.rideSecs > 0 ? S.rideMiles / (S.rideSecs / 3600.0) : 0, 1) + " mph",
                String(S.topMph, 0) + " mph"};
  for (int i = 0; i < 5; i++) {
    spr.setTextColor(COL_GREY); spr.drawString(k[i], 10, 70 + i * 24, 2);
    spr.setTextColor(TFT_WHITE); spr.drawRightString(v[i], 310, 70 + i * 24, 2);
  }
  drawBottom("Hold MODE: reset trip A", "");
}

void drawSystem() {
  spr.setTextColor(COL_AMBER); spr.drawString("SYSTEM", 10, 42, 2);
  uint16_t vc = S.volts < 12.2f ? COL_RED : S.volts < 12.8f ? COL_AMBER : COL_GREEN;
  spr.setTextColor(COL_GREY); spr.drawString("SUPPLY", 10, 70, 2);
  spr.setTextColor(vc); spr.drawRightString(String(S.volts, 1) + " V", 150, 70, 2);
  spr.setTextColor(COL_GREY); spr.drawString("GPS", 10, 94, 2);
  spr.setTextColor(TFT_WHITE); spr.drawRightString(S.gpsOk ? String(S.sats) + " sats" : "no fix", 150, 94, 2);
  spr.setTextColor(COL_GREY); spr.drawString("WIFI", 10, 118, 2);
  spr.setTextColor(TFT_WHITE); spr.drawRightString(apOn ? "on" : "off", 150, 118, 2);
  const char* names[] = {"1 IND L", "2 IND R", "3 LOW", "4 HIGH", "5 HORN", "6 USB", "7 AUX", "8 SPARE"};
  for (int i = 0; i < 8; i++) {
    int y = 66 + i * 16;
    spr.fillRect(176, y + 2, 10, 10, S.outState[i] ? COL_GREEN : COL_DIM);
    spr.setTextColor(S.outState[i] ? TFT_WHITE : COL_GREY);
    spr.drawString(names[i], 194, y, 2);
  }
  drawBottom("Outputs live", "");
}

void drawScreen() {
  spr.fillSprite(TFT_BLACK);
  drawTop();
  if (S.screen == 0) drawRide(); else if (S.screen == 1) drawTrip(); else drawSystem();
  if (S.horn) { spr.fillRect(110, 186, 100, 18, COL_AMBER); spr.setTextColor(TFT_BLACK); spr.drawCentreString("HORN", 160, 187, 2); }
  spr.pushSprite(0, 0);
}

// ------------------------------------------------------------------ WiFi page
const char PAGE[] PROGMEM = R"HTML(<!doctype html><meta name=viewport content="width=device-width">
<title>XL dash</title><style>body{font-family:sans-serif;background:#111;color:#eee;margin:16px}
button{padding:10px 14px;margin:4px;border:0;border-radius:8px;background:#333;color:#fff}
.on{background:#2a7}</style><h2>XL125R box</h2><pre id=s></pre><h3>Test outputs</h3><div id=o></div>
<h3>Firmware update</h3><form method=POST action=/update enctype=multipart/form-data>
<input type=file name=f><button>Upload .bin</button></form>
<script>const n=['IND L','IND R','LOW','HIGH','HORN','USB','AUX','SPARE'];
async function t(){const r=await fetch('/api/state');const j=await r.json();
document.getElementById('s').textContent=`RPM ${j.rpm}  MPH ${j.mph}  ${j.volts} V\nGPS ${j.sats} sats ${j.gps?'fix':'no fix'}  ODO ${j.odo}`;
document.getElementById('o').innerHTML=n.map((x,i)=>`<button class="${j.out[i]?'on':''}" onclick="fetch('/api/test?n=${i}')">${i+1} ${x}</button>`).join('');}
setInterval(t,500);t();</script>)HTML";

void startAP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  web.on("/", [] { web.send_P(200, "text/html", PAGE); });
  web.on("/api/state", [] {
    String j = "{\"rpm\":" + String((int)S.rpm) + ",\"mph\":" + String(S.mph, 1) +
               ",\"volts\":" + String(S.volts, 2) + ",\"sats\":" + String(S.sats) +
               ",\"gps\":" + String(S.gpsOk ? "true" : "false") + ",\"odo\":" + String(S.odo, 1) + ",\"out\":[";
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
  for (Button* b : buttons) pinMode(b->pin, INPUT_PULLUP);
  pinMode(PIN_RPM, INPUT);                       // filter sets the level (input-only pin)
  pinMode(PIN_BRAKE, INPUT);                     // opto needs an external 10k pull-up
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), rpmISR, RISING);
  analogSetPinAttenuation(PIN_VOLTS, ADC_11db);

  prefs.begin("xl", false);
  S.odo = prefs.getDouble("odo", 0); S.tripA = prefs.getDouble("tripA", 0); S.tripB = prefs.getDouble("tripB", 0);
  lastSavedOdo = S.odo;

  GPSSerial.begin(GPS_BAUD, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);

  tft.init(); tft.setRotation(1); tft.fillScreen(TFT_BLACK);
  ledcSetup(0, 5000, 8); ledcAttachPin(PIN_TFT_BL, 0); ledcWrite(0, 255);
  spr.setColorDepth(8);                          // 75 KB frame, fits without PSRAM
  spr.createSprite(320, 240);

  writeOutputs();                                // low beam on straight away
  startAP();
}

uint32_t lastDraw = 0, lastSlow = 0;
void loop() {
  handleButtons();
  updateRpm();
  writeOutputs();
  updateGpsAndOdo();
  if (millis() - lastSlow > 50) { lastSlow = millis(); updateVolts(); }
  if (millis() - lastDraw > 50) { lastDraw = millis(); drawScreen(); }   // ~20 fps
  if (apOn) {
    web.handleClient();
    if (millis() - apStartMs > AP_TIMEOUT_MS || S.mph > AP_OFF_ABOVE_MPH) stopAP();
  }
}
