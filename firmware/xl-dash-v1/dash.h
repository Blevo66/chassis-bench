// XL125R dash v1: all the code. Settings and pins are in config.h.
#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <math.h>
#include <string.h>
#include <esp_heap_caps.h>
#include <Arduino_GFX_Library.h>
#include "TCA9554.h"
#include "config.h"
#include "fonts.h"

// ---- Waveshare pins (from their 08_gfx_helloworld example) ----
#define PIN_BL 6
#define PIN_SCLK 5
#define PIN_MOSI 1
#define PIN_MISO 2
#define PIN_DC 3
#define PIN_SDA 8
#define PIN_SCL 7
#define TOUCH_ADDR 0x38

static const int W = 480, H = 320;

static TCA9554 TCA(0x20);
static Arduino_DataBus *bus = new Arduino_ESP32SPI(PIN_DC, -1 /*CS*/, PIN_SCLK, PIN_MOSI, PIN_MISO);
static Arduino_GFX *lcd = new Arduino_ST7796(bus, -1 /*RST*/, SCREEN_ROTATION, true /*IPS*/, 320, 480);

// ------------------------------------------------------------------ colours
static constexpr uint16_t RGB(uint8_t r, uint8_t g, uint8_t b) {
  return (uint16_t)(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3));
}
static const uint16_t C_BG = RGB(34, 38, 48);  
static const uint16_t C_OFF = RGB(62, 67, 80);    // unlit icons / segments
static const uint16_t C_RING = RGB(58, 63, 76);   // unlit dial band
static const uint16_t C_REDZ = RGB(96, 28, 30);   // unlit red zone
static const uint16_t C_DIM = RGB(105, 110, 124);
static const uint16_t C_GREY = RGB(140, 146, 158);
static const uint16_t C_TXT = RGB(238, 240, 245);
static const uint16_t C_COOL = RGB(200, 225, 255);
static const uint16_t C_AMB = RGB(255, 170, 0);
static const uint16_t C_RED = RGB(255, 48, 36);
static const uint16_t C_GRN = RGB(40, 220, 90);
static const uint16_t C_BLU = RGB(60, 140, 255);
static const uint16_t C_NEEDLE = RGB(255, 84, 30);

// 0..255 alpha blend of RGB565 (classic 5-bit trick)
static inline uint16_t blend565(uint16_t b, uint16_t f, uint8_t a) {
  if (a == 0) return b;
  if (a >= 252) return f;
  uint32_t a5 = (a + 4) >> 3;
  uint32_t bx = (b | ((uint32_t)b << 16)) & 0x07E0F81F;
  uint32_t fx = (f | ((uint32_t)f << 16)) & 0x07E0F81F;
  uint32_t r = ((((fx - bx) * a5) >> 5) + bx) & 0x07E0F81F;
  return (uint16_t)(r | (r >> 16));
}

// ------------------------------------------------------------------ rects
struct Rect { int16_t x, y, w, h; };
static inline bool rEmpty(const Rect &r) { return r.w <= 0 || r.h <= 0; }
static Rect rUnion(const Rect &a, const Rect &b) {
  if (rEmpty(a)) return b;
  if (rEmpty(b)) return a;
  int x0 = min(a.x, b.x), y0 = min(a.y, b.y);
  int x1 = max(a.x + a.w, b.x + b.w), y1 = max(a.y + a.h, b.y + b.h);
  return Rect{(int16_t)x0, (int16_t)y0, (int16_t)(x1 - x0), (int16_t)(y1 - y0)};
}
static Rect rClip(const Rect &a) {
  int x0 = max<int>(a.x, 0), y0 = max<int>(a.y, 0);
  int x1 = min<int>(a.x + a.w, W), y1 = min<int>(a.y + a.h, H);
  return Rect{(int16_t)x0, (int16_t)y0, (int16_t)(x1 - x0), (int16_t)(y1 - y0)};
}
static inline int32_t rArea(const Rect &r) { return rEmpty(r) ? 0 : (int32_t)r.w * r.h; }
static Rect rPad(Rect r, int p) { r.x -= p; r.y -= p; r.w += 2 * p; r.h += 2 * p; return r; }

// ------------------------------------------------------------------ buffers
// fb = what's on the screen. bg[p] = static parts of page p, used to wipe
// a widget before redrawing it. All in PSRAM. xfer = small internal-RAM
// buffer used to send dirty rectangles to the screen.
static const int NPAGES = 4;   // ride, trip, system, test
static uint16_t *fb, *bg[NPAGES], *oldBuf, *pageBuf, *xfer;
static const int XFER_PIX = W * 20;

static uint16_t *T;                       // current draw target (W x H)
static int clipX0 = 0, clipY0 = 0, clipX1 = W, clipY1 = H;
static void setClip(const Rect &r) {
  Rect c = rClip(r);
  clipX0 = c.x; clipY0 = c.y; clipX1 = c.x + max<int>(c.w, 0); clipY1 = c.y + max<int>(c.h, 0);
}
static void clipAll() { clipX0 = 0; clipY0 = 0; clipX1 = W; clipY1 = H; }

static inline void blendPx(int x, int y, uint16_t c, uint8_t a) {
  if (x < clipX0 || y < clipY0 || x >= clipX1 || y >= clipY1 || a == 0) return;
  uint16_t *p = T + y * W + x;
  *p = blend565(*p, c, a);
}
static void fillRect(int x, int y, int w, int h, uint16_t c) {
  int x0 = max(x, clipX0), y0 = max(y, clipY0), x1 = min(x + w, clipX1), y1 = min(y + h, clipY1);
  for (int j = y0; j < y1; j++) { uint16_t *p = T + j * W; for (int i = x0; i < x1; i++) p[i] = c; }
}
static void hline(int x, int y, int w, uint16_t c) { fillRect(x, y, w, 1, c); }

// ------------------------------------------------ anti-aliased shapes
// Thick line with round ends (also does discs when the ends are the same point)
static void capsule(float ax, float ay, float bx, float by, float r, uint16_t c, uint8_t alpha = 255) {
  int x0 = max((int)floorf(min(ax, bx) - r - 1), clipX0), x1 = min((int)ceilf(max(ax, bx) + r + 1), clipX1);
  int y0 = max((int)floorf(min(ay, by) - r - 1), clipY0), y1 = min((int)ceilf(max(ay, by) + r + 1), clipY1);
  float dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy;
  float rin = max(r - 0.5f, 0.0f), rout = r + 0.5f;
  for (int y = y0; y < y1; y++) {
    for (int x = x0; x < x1; x++) {
      float px = x + 0.5f - ax, py = y + 0.5f - ay;
      float t = L2 > 0 ? (px * dx + py * dy) / L2 : 0;
      t = t < 0 ? 0 : (t > 1 ? 1 : t);
      float ex = px - t * dx, ey = py - t * dy, d2 = ex * ex + ey * ey;
      if (d2 >= rout * rout) continue;
      uint8_t a = alpha;
      if (d2 > rin * rin) a = (uint8_t)(alpha * (rout - sqrtf(d2)));
      blendPx(x, y, c, a);
    }
  }
}
static void disc(float cx, float cy, float r, uint16_t c, uint8_t a = 255) { capsule(cx, cy, cx, cy, r, c, a); }

// Convex polygon (needle, arrows). Edge coverage from distance to each edge.
static void convexPoly(const float *xs, const float *ys, int n, uint16_t c, uint8_t alpha = 255) {
  float nx[8], ny[8], cx = 0, cy = 0;
  float bx0 = 1e9, by0 = 1e9, bx1 = -1e9, by1 = -1e9;
  for (int i = 0; i < n; i++) {
    cx += xs[i] / n; cy += ys[i] / n;
    bx0 = min(bx0, xs[i]); bx1 = max(bx1, xs[i]); by0 = min(by0, ys[i]); by1 = max(by1, ys[i]);
  }
  for (int i = 0; i < n; i++) {
    int j = (i + 1) % n;
    float ex = xs[j] - xs[i], ey = ys[j] - ys[i], L = sqrtf(ex * ex + ey * ey);
    if (L < 1e-4f) L = 1e-4f;
    nx[i] = -ey / L; ny[i] = ex / L;
    if ((cx - xs[i]) * nx[i] + (cy - ys[i]) * ny[i] < 0) { nx[i] = -nx[i]; ny[i] = -ny[i]; }
  }
  int x0 = max((int)floorf(bx0) - 1, clipX0), x1 = min((int)ceilf(bx1) + 1, clipX1);
  int y0 = max((int)floorf(by0) - 1, clipY0), y1 = min((int)ceilf(by1) + 1, clipY1);
  for (int y = y0; y < y1; y++) {
    for (int x = x0; x < x1; x++) {
      float px = x + 0.5f, py = y + 0.5f, m = 1e9;
      for (int i = 0; i < n; i++) {
        float d = (px - xs[i]) * nx[i] + (py - ys[i]) * ny[i];
        if (d < m) m = d;
        if (m <= -0.5f) break;
      }
      if (m <= -0.5f) continue;
      float cov = m + 0.5f;
      blendPx(x, y, c, cov >= 1 ? alpha : (uint8_t)(alpha * cov));
    }
  }
}

// Angles are degrees, 0 = pointing right, increasing CLOCKWISE (screen y is down).
static Rect arcBox(float cx, float cy, float r0, float r1, float a0, float a1) {
  float xs = 1e9, ys = 1e9, xe = -1e9, ye = -1e9;
  auto add = [&](float a, float r) {
    float x = cx + cosf(a * DEG_TO_RAD) * r, y = cy + sinf(a * DEG_TO_RAD) * r;
    xs = min(xs, x); xe = max(xe, x); ys = min(ys, y); ye = max(ye, y);
  };
  add(a0, r0); add(a0, r1); add(a1, r0); add(a1, r1);
  for (float k = ceilf(a0 / 90) * 90; k < a1; k += 90) add(k, r1);
  return rPad(Rect{(int16_t)floorf(xs), (int16_t)floorf(ys), (int16_t)(ceilf(xe) - floorf(xs) + 1), (int16_t)(ceilf(ye) - floorf(ys) + 1)}, 2);
}

// Ring sector between radii r0..r1 and angles a0..a1, smooth on all four edges
static void ringSeg(float cx, float cy, float r0, float r1, float a0, float a1, uint16_t c, uint8_t alpha = 255) {
  if (a1 <= a0) return;
  Rect b = arcBox(cx, cy, r0, r1, a0, a1);
  int x0 = max<int>(b.x, clipX0), x1 = min<int>(b.x + b.w, clipX1);
  int y0 = max<int>(b.y, clipY0), y1 = min<int>(b.y + b.h, clipY1);
  float lo2 = (r0 - 1) * (r0 - 1), hi2 = (r1 + 1) * (r1 + 1);
  for (int y = y0; y < y1; y++) {
    float dy = y + 0.5f - cy;
    for (int x = x0; x < x1; x++) {
      float dx = x + 0.5f - cx, d2 = dx * dx + dy * dy;
      if (d2 < lo2 || d2 > hi2) continue;
      float d = sqrtf(d2);
      float cr = min(d - r0, r1 - d) + 0.5f;
      if (cr <= 0) continue;
      float ang = atan2f(dy, dx) * RAD_TO_DEG;
      while (ang < a0) ang += 360;
      while (ang >= a0 + 360) ang -= 360;
      float inside = (ang <= a1) ? min(ang - a0, a1 - ang) : -min(ang - a1, a0 + 360 - ang);
      float ca = inside * DEG_TO_RAD * d + 0.5f;
      if (ca <= 0) continue;
      float cov = min(cr, 1.0f) * min(ca, 1.0f);
      blendPx(x, y, c, (uint8_t)(alpha * cov));
    }
  }
}

// ------------------------------------------------------------------ text
static int glyphIndex(const AAFont &f, char ch) {
  if (!f.map) { int i = ch - 32; return (i >= 0 && i < f.count) ? i : -1; }
  const char *p = strchr(f.map, ch);
  return (p && ch) ? (int)(p - f.map) : -1;
}
static int textWidth(const AAFont &f, const char *s) {
  int w = 0;
  for (; *s; s++) { int i = glyphIndex(f, *s); if (i >= 0) w += f.g[i].adv; }
  return w;
}
enum { LEFT = 0, CENTRE = 1, RIGHT = 2 };
// y is the BASELINE
static void text(const AAFont &f, int x, int y, const char *s, uint16_t c, int align = LEFT) {
  if (align == CENTRE) x -= textWidth(f, s) / 2;
  else if (align == RIGHT) x -= textWidth(f, s);
  for (; *s; s++) {
    int gi = glyphIndex(f, *s);
    if (gi < 0) continue;
    const AAGlyph &g = f.g[gi];
    const uint8_t *bmp = f.bmp + g.off;
    int gx = x + g.xo, gy = y + g.yo;
    if (gx + g.w > clipX0 && gx < clipX1 && gy + g.h > clipY0 && gy < clipY1) {
      for (int j = 0; j < g.h; j++) {
        for (int i = 0; i < g.w; i++) {
          int k = j * g.w + i;
          uint8_t nib = (bmp[k >> 1] >> ((k & 1) ? 0 : 4)) & 15;
          if (nib) blendPx(gx + i, gy + j, c, nib * 17);
        }
      }
    }
    x += g.adv;
  }
}

// Text with a dark outline so it stays readable over the stripes
static void textOutlined(const AAFont &f, int x, int y, const char *s, uint16_t c, int align = LEFT) {
  for (int dy = -2; dy <= 2; dy++)
    for (int dx = -2; dx <= 2; dx++)
      if (dx || dy) text(f, x + dx, y + dy, s, C_BG, align);
  text(f, x, y, s, c, align);
}

// ------------------------------------------------------------------ dirty list + flush
static Rect dirty[24];
static int nDirty = 0;
static bool collectDirty = true;
static uint32_t statPx = 0;          // pixels sent this second

static void addDirty(Rect r) {
  if (!collectDirty) return;
  r = rClip(r);
  if (rEmpty(r)) return;
  for (int i = 0; i < nDirty; i++) {
    Rect u = rUnion(dirty[i], r);
    if (rArea(u) <= (rArea(dirty[i]) + rArea(r)) * 5 / 4) { dirty[i] = u; return; }
  }
  if (nDirty < 24) dirty[nDirty++] = r;
  else dirty[23] = rUnion(dirty[23], r);
}

static void sendRect(const Rect &r) {
  int rows = max(1, XFER_PIX / r.w);
  for (int y = r.y; y < r.y + r.h; y += rows) {
    int n = min(rows, r.y + r.h - y);
    for (int j = 0; j < n; j++) memcpy(xfer + j * r.w, fb + (y + j) * W + r.x, r.w * 2);
    lcd->draw16bitRGBBitmap(r.x, y, xfer, r.w, n);
  }
  statPx += (uint32_t)r.w * r.h;
}

static void flushDirty() {
  int32_t total = 0;
  for (int i = 0; i < nDirty; i++) total += rArea(dirty[i]);
  if (total > W * H * 7 / 10) sendRect(Rect{0, 0, W, H});
  else for (int i = 0; i < nDirty; i++) sendRect(dirty[i]);
  nDirty = 0;
}

// ------------------------------------------------------------------ state
struct Ride {
  float rpm = 0, mph = 0;
  int gear = 0;
  bool indL = false, indR = false, beam = false, brake = false;
  bool hazard = false, high = false, flash = false, horn = false;
  bool lightsOn = false;          // headlight OFF at power-up (hold LIGHTS to turn on)
  bool drl = true;                // DRL / sidelight on OUT7, always on with the ignition
  bool out[8] = {};               // what each MOSFET output is doing right now
  uint8_t btn = 0;                // bit n = MCP pin n pressed (raw, live)
  int mcpAddr = -1;               // where the button chip was found, -1 = not found
  bool supplyOn = true, charging = false; float lipoV = 0; int lipoPct = -1;
  double odo = 4817.3, tripA = 0, tripB = 212.6;
  float maxMph = 0, rideS = 0, movingS = 0;
  float battV = 12.6f, ignV = 12.4f;
} S;

static float showRpm = 0, rpmVel = 0, showMph = 0, mphVel = 0;
static int page = 0;
static bool touchOk = false;
static int16_t touchX = -1, touchY = -1;
static uint32_t bootMs = 0;
static int fps = 0;
static float drawMs = 0, sendMs = 0, sentPct = 0;

// GPS (real, if wired)
struct Gps { bool seen = false, fix = false, timeOk = false; int sats = 0; float mph = 0; uint32_t lastMs = 0, lastFixMs = 0;
             int hh = 0, mm = 0, ss = 0, day = 0, mon = 0, yr = 0; uint32_t timeMs = 0; } G;
static bool gpsLive() { return G.fix && millis() - G.lastFixMs < 3000; }

// Unity-style critically damped spring: smooth, no overshoot
static float smoothDamp(float cur, float target, float &vel, float smoothTime, float dt) {
  float omega = 2.0f / smoothTime, x = omega * dt;
  float e = 1.0f / (1.0f + x + 0.48f * x * x + 0.235f * x * x * x);
  float change = cur - target, temp = (vel + omega * change) * dt;
  vel = (vel - omega * temp) * e;
  return target + (change + temp) * e;
}

// ------------------------------------------------------------------ fake ride
static const float RATIO[6] = {0, 450, 300, 225, 180, 150};   // rpm per mph (same placeholders as config.h)
enum Phase { BOOT_SWEEP, STOPPED, ACCEL, CRUISE, BRAKING };
static Phase phase = BOOT_SWEEP;
static float phaseT = 0;

static void simulate(float dt) {
  phaseT += dt;
  float t = millis() * 0.001f;
  float idle = 1450 + sinf(t * 7.0f) * 35 + sinf(t * 2.3f) * 25;
  switch (phase) {
    case BOOT_SWEEP: {                     // needle sweep self-test
      float u = phaseT;
      S.rpm = u < 0.55f ? RPM_MAX * (u / 0.55f) : u < 0.75f ? RPM_MAX : u < 1.4f ? RPM_MAX * (1 - (u - 0.75f) / 0.65f) : idle;
      S.indL = S.indR = S.beam = S.brake = u < 1.2f;
      S.gear = 0;
      if (u > 1.8f) { phase = STOPPED; phaseT = 0; }
      break;
    }
    case STOPPED:
      S.gear = 0; S.brake = false; S.beam = false; S.indL = false;
      S.mph = 0; S.rpm = idle;
      S.indR = phaseT > 1.2f && phaseT < 4.0f;          // indicate before pulling out
      if (phaseT > 2.6f && phaseT < 2.9f) S.rpm = 1450 + 4500 * sinf((phaseT - 2.6f) / 0.3f * PI);  // throttle blip
      if (phaseT > 4.0f) { phase = ACCEL; phaseT = 0; S.gear = 1; S.rpm = 2600; S.indR = false; }
      break;
    case ACCEL: {
      float rate = 7000.0f / powf((float)S.gear, 0.75f);
      S.rpm += rate * dt;
      float shiftAt = (S.gear == 2) ? 10200 : 9000;    // 2nd gear over-revs to show the shift light
      if (S.rpm > shiftAt && S.gear < 5) { float v = S.rpm / RATIO[S.gear]; S.gear++; S.rpm = v * RATIO[S.gear]; }
      S.mph = S.rpm / RATIO[S.gear];
      if (S.gear == 5 && S.mph > 58) { phase = CRUISE; phaseT = 0; }
      break;
    }
    case CRUISE:
      S.beam = true;
      S.rpm = 8800 + sinf(phaseT * 1.1f) * 300 + sinf(phaseT * 5.3f) * 60;
      S.mph = S.rpm / RATIO[S.gear];
      S.indL = phaseT > 2.5f && phaseT < 6.0f;           // overtake
      if (phaseT > 8.0f) { phase = BRAKING; phaseT = 0; S.indL = false; S.beam = false; }
      break;
    case BRAKING:
      S.brake = true;
      S.mph -= 11.0f * dt;
      if (S.mph < 0) S.mph = 0;
      if (S.gear > 0) S.rpm = S.mph * RATIO[S.gear];
      if (S.gear > 1 && S.rpm < 4200) { S.gear--; S.rpm = S.mph * RATIO[S.gear]; }   // blip down a gear
      if (S.gear == 1 && S.rpm < 2200) S.gear = 0;
      if (S.gear == 0) S.rpm = idle;
      if (S.mph <= 0.3f) { phase = STOPPED; phaseT = 0; S.mph = 0; }
      break;
  }
  S.battV = (S.rpm > 3000 ? 13.9f : 12.7f) + sinf(t * 0.7f) * 0.05f;
  S.ignV = 12.35f - S.rideS * 0.00002f;
}

// ------------------------------------------------------------------ GPS (NMEA RMC + GGA)
#if GPS_RX_PIN >= 0
static char nmea[100];
static int nmeaLen = 0;
static int nmeaField(const char *s, int n, char *out, int outLen) {   // copy field n (0 = talker)
  int f = 0, k = 0;
  for (; *s && *s != '*'; s++) {
    if (*s == ',') { if (f == n) break; f++; continue; }
    if (f == n && k < outLen - 1) out[k++] = *s;
  }
  out[k] = 0;
  return k;
}
static void nmeaLine(const char *s) {
  if (strlen(s) < 7 || s[0] != '$') return;
  char f[20];
  G.seen = true; G.lastMs = millis();
  if (!strncmp(s + 3, "RMC", 3)) {
    char tm[20], dt[20];
    nmeaField(s, 1, tm, sizeof tm);
    nmeaField(s, 9, dt, sizeof dt);
    if (strlen(tm) >= 6 && strlen(dt) == 6) {
      G.hh = (tm[0] - '0') * 10 + tm[1] - '0'; G.mm = (tm[2] - '0') * 10 + tm[3] - '0'; G.ss = (tm[4] - '0') * 10 + tm[5] - '0';
      G.day = (dt[0] - '0') * 10 + dt[1] - '0'; G.mon = (dt[2] - '0') * 10 + dt[3] - '0'; G.yr = 2000 + (dt[4] - '0') * 10 + dt[5] - '0';
      G.timeOk = true; G.timeMs = millis();
    }
    nmeaField(s, 2, f, sizeof f);
    bool ok = f[0] == 'A';
    nmeaField(s, 7, f, sizeof f);
    if (ok) { G.fix = true; G.lastFixMs = millis(); G.mph = atof(f) * 1.15078f; }
    else G.fix = false;
  } else if (!strncmp(s + 3, "GGA", 3)) {
    nmeaField(s, 7, f, sizeof f);
    G.sats = atoi(f);
  }
}
static void pollGps() {
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n' || c == '\r') { if (nmeaLen) { nmea[nmeaLen] = 0; nmeaLine(nmea); nmeaLen = 0; } }
    else if (nmeaLen < (int)sizeof(nmea) - 1) nmea[nmeaLen++] = c;
    else nmeaLen = 0;
  }
}
#else
static void pollGps() {}
#endif


// ------------------------------------------------------------------ real inputs and outputs
static bool i2cWrite(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
static int i2cRead(uint8_t addr, uint8_t reg) {          // -1 if the chip didn't answer
  Wire.beginTransmission(addr); Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(addr, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

// MCP23017: all of port A inputs with pull-ups; pressed = LOW. Searched for at 0x21-0x27.
static void mcpFind() {
  S.mcpAddr = -1;
  for (int a = 0x21; a <= 0x27; a++) {
    if (i2cWrite(a, 0x00, 0xFF) && i2cWrite(a, 0x0C, 0xFF)) {   // IODIRA = inputs, GPPUA = pull-ups
      int v = i2cRead(a, 0x00);
      if (v == 0xFF) { S.mcpAddr = a; break; }
    }
  }
  if (S.mcpAddr < 0) Serial.println("Button chip (MCP23017) not found at 0x21-0x27");
  else Serial.printf("Button chip (MCP23017) found at 0x%02X\n", S.mcpAddr);
}
static void mcpRead() {
  static uint32_t lastTry = 0, lastRead = 0;
  if (S.mcpAddr < 0) {
    S.btn = 0;
    if (millis() - lastTry > 2000) { lastTry = millis(); mcpFind(); }   // plugged in later? keep looking
    return;
  }
  if (millis() - lastRead < 5) return;
  lastRead = millis();
  int v = i2cRead(S.mcpAddr, 0x12);                       // GPIOA
  if (v < 0) { S.mcpAddr = -1; S.btn = 0; lastTry = millis(); return; }
  S.btn = (uint8_t)~v;
}

struct Button { int pin; bool down = false, held = false, lastRaw = false; uint32_t changedMs = 0, downMs = 0; };
static Button bL{BTN_IND_L}, bR{BTN_IND_R}, bHorn{BTN_HORN}, bLights{BTN_LIGHTS}, bMode{BTN_MODE};
// 0 nothing, 1 tap (on release), 2 hold reached
static int pollButton(Button &b) {
  bool raw = S.btn & (1 << b.pin);
  uint32_t now = millis();
  if (raw != b.lastRaw) { b.lastRaw = raw; b.changedMs = now; }
  if (now - b.changedMs < DEBOUNCE_MS) return 0;
  if (raw && !b.down) { b.down = true; b.held = false; b.downMs = now; }
  if (raw && b.down && !b.held && now - b.downMs >= HOLD_MS) { b.held = true; return 2; }
  if (!raw && b.down) { b.down = false; if (!b.held) return 1; }
  return 0;
}

static Preferences prefs;
static double lastSavedOdo = 0;
static void saveTrips() {
  prefs.putDouble("odo", S.odo); prefs.putDouble("tripA", S.tripA); prefs.putDouble("tripB", S.tripB);
  lastSavedOdo = S.odo;
}

static int pendingPage = 0;      // set by the MODE button, acted on in the loop
static char lastEvent[48] = "press a button";   // shown on the TEST page and printed to Serial
static uint32_t eventCount = 0;
static void logEvent(const char *s) {
  snprintf(lastEvent, sizeof lastEvent, "%s", s); eventCount++;
  Serial.printf("[button] %s\n", s);
}
static void handleButtons() {
  mcpRead();
  int e;
  if ((e = pollButton(bL))) {
    if (e == 1) { S.hazard = false; S.indR = false; S.indL = !S.indL; logEvent(S.indL ? "IND L tap = left ON" : "IND L tap = left off"); }
    else        { S.hazard = !S.hazard; S.indL = S.indR = false; logEvent(S.hazard ? "IND L hold = hazards ON" : "IND L hold = hazards off"); }
  }
  if ((e = pollButton(bR))) {
    if (e == 1) { S.hazard = false; S.indL = false; S.indR = !S.indR; logEvent(S.indR ? "IND R tap = right ON" : "IND R tap = right off"); }
    else        { S.hazard = !S.hazard; S.indL = S.indR = false; logEvent(S.hazard ? "IND R hold = hazards ON" : "IND R hold = hazards off"); }
  }
  if (pollButton(bHorn) == 1) logEvent("HORN pressed");
  S.horn = S.btn & (1 << BTN_HORN);                       // straight from the switch, no delay
  uint32_t now = millis();

  // LIGHTS: hold LIGHTS_OFF_MS = headlight on (low beam) / off. Tap = high / low, only while it's on.
  // The DRL is always on; writeOutputs() dims it when the headlight is on.
  static bool lightsDone = false;
  if (pollButton(bLights) == 1) {
    if (!S.lightsOn) logEvent("LIGHTS tap: headlight off, hold 3 s");
    else { S.high = !S.high; logEvent(S.high ? "LIGHTS tap = HIGH beam" : "LIGHTS tap = low beam"); }
  }
  if (!bLights.down) lightsDone = false;
  else if (!lightsDone && now - bLights.downMs >= LIGHTS_OFF_MS) {
    S.lightsOn = !S.lightsOn; S.high = false; lightsDone = true;
    logEvent(S.lightsOn ? "LIGHTS hold 3 s = headlight ON (low)" : "LIGHTS hold 3 s = headlight OFF");
  }

  // MODE: tap = flash the high beam for PASS_FLASH_MS, hold = next page.
  // On the TRIP page: hold and let go = next page, keep holding TRIP_RESET_MS = reset trip A.
  static uint32_t passUntil = 0;
  static bool modeWaiting = false;
  if ((e = pollButton(bMode))) {
    if (e == 1) { passUntil = now + PASS_FLASH_MS; logEvent("MODE tap = flash high beam"); }
    else if (page == 1) modeWaiting = true;
    else { pendingPage = +1; logEvent("MODE hold = next page"); }
  }
  if (modeWaiting) {
    if (!bMode.down) { modeWaiting = false; pendingPage = +1; logEvent("MODE hold = next page"); }
    else if (now - bMode.downMs >= TRIP_RESET_MS) {
      modeWaiting = false;
      S.tripA = 0; S.maxMph = 0; S.rideS = 0; S.movingS = 0; saveTrips();
      logEvent("MODE hold 3 s = trip A RESET");
    }
  }
  S.flash = (int32_t)(passUntil - now) > 0;
}

static bool flashPhase() { return (millis() % FLASH_PERIOD_MS) < FLASH_PERIOD_MS / 2; }
static void writeOutputs() {
  bool f = flashPhase(), w[8];
  w[O_IND_L] = (S.indL || S.hazard) && f;
  w[O_IND_R] = (S.indR || S.hazard) && f;
  bool highOn = (S.lightsOn && S.high) || S.flash;   // flash works even with the lights off
  w[O_HIGH] = highOn;
  w[O_LOW] = S.lightsOn && (!highOn || LOW_WITH_HIGH);
  w[O_HORN] = S.horn;
  w[O_USB] = true;
  w[O_AUX] = S.drl;                                    // DRL: full by day, dimmed with the headlight
  w[O_TAIL] = true;
  for (int i = 0; i < 8; i++) {
    S.out[i] = w[i];
    if (PIN_OUT[i] < 0) continue;
    if (i == O_TAIL || i == O_AUX) {
      float d = !w[i] ? 0.0f : (i == O_TAIL) ? TAIL_DUTY : (S.lightsOn ? DRL_DIM_DUTY : 1.0f);
      if (!OUT_ACTIVE_HIGH) d = 1.0f - d;
      ledcWrite(PIN_OUT[i], (uint32_t)(d * 255.0f + 0.5f));
    } else digitalWrite(PIN_OUT[i], w[i] == OUT_ACTIVE_HIGH ? HIGH : LOW);
  }
  S.beam = highOn;
}

// Brake: the opto sees lamp - at earth. Tail PWM pulls it low only TAIL_DUTY of the time,
// the brake switch holds it low, so brake = LOW for a whole PWM period.
static void readBrake() {
  const uint32_t stepUs = (1300000UL / TAIL_PWM_HZ) / 16;
  for (int i = 0; i < 16; i++) {
    if (digitalRead(PIN_BRAKE) != LOW) { S.brake = false; return; }
    delayMicroseconds(stepUs);
  }
  S.brake = true;
}

static volatile uint32_t rpmLastUs = 0, rpmPeriodUs = 0;
static void IRAM_ATTR rpmISR() {
  uint32_t now = micros(), dt = now - rpmLastUs;
  if (dt < RPM_LOCKOUT_US) return;
  rpmPeriodUs = dt; rpmLastUs = now;
}
static void updateRpm() {
  noInterrupts(); uint32_t period = rpmPeriodUs, last = rpmLastUs; interrupts();
  S.rpm = (period > 0 && (micros() - last) < RPM_TIMEOUT_MS * 1000UL) ? 60.0e6f / (period * SPARKS_PER_REV) : 0;
}

// AXP2101 power chip (registers from XPowersLib's map, NOT yet checked on this board)
static void axpRead() {
  const uint8_t A = 0x34;
  int st1 = i2cRead(A, 0x00), st2 = i2cRead(A, 0x01);
  if (st1 < 0) return;
  S.supplyOn = st1 & 0x20;
  bool battIn = st1 & 0x08;
  S.charging = st2 >= 0 && ((st2 >> 5) & 0x03) == 0x01;
  int h = i2cRead(A, 0x34), l = i2cRead(A, 0x35);
  S.lipoV = (battIn && h >= 0 && l >= 0) ? (((h & 0x1F) << 8) | l) / 1000.0f : 0;
  int pct = i2cRead(A, 0xA4);
  S.lipoPct = (battIn && pct >= 0 && pct <= 100) ? pct : -1;
}

static void realUpdate(float dt) {
  updateRpm();
  readBrake();
  S.mph = (gpsLive() && G.mph >= GPS_STILL_MPH) ? G.mph : 0;
  if (S.mph > 2) {
    double mi = S.mph * dt / 3600.0;
    S.odo += mi; S.tripA += mi; S.tripB += mi; S.movingS += dt;
    if (S.mph > S.maxMph) S.maxMph = S.mph;
  }
  S.rideS += dt;
  if (S.odo - lastSavedOdo >= 0.1) saveTrips();
  S.gear = 0;                                        // gear from rpm / speed, nearest within 15%
  if (S.mph > 3 && S.rpm > 1000) {
    float r = S.rpm / S.mph, best = 1e9;
    for (int g = 1; g <= 5; g++) {
      float err = fabsf(r - GEAR_RPM_PER_MPH[g]) / GEAR_RPM_PER_MPH[g];
      if (err < 0.15f && err < best) { best = err; S.gear = g; }
    }
  }
  static uint32_t lastAxp = 0;
  static bool savedOnDrop = false;
  if (millis() - lastAxp > 500) {
    lastAxp = millis(); axpRead();
    if (!S.supplyOn && !savedOnDrop) { saveTrips(); savedOnDrop = true; }
    if (S.supplyOn) savedOnDrop = false;
  }
}

// UK time from GPS UTC (BST: last Sunday of March 01:00 UTC to last Sunday of October 01:00 UTC)
static int dow(int y, int m, int d) { static const int t[] = {0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4}; if (m < 3) y--; return (y + y / 4 - y / 100 + y / 400 + t[m - 1] + d) % 7; }
static int lastSunday(int y, int m) { int d = 31; while (dow(y, m, d) != 0) d--; return d; }
static bool ukClock(int &hh, int &mm) {
  if (!G.timeOk || millis() - G.timeMs > 5000) return false;
  int h = G.hh, m = G.mm;
  int mo = G.mon, d = G.day;
  bool bst = (mo > 3 && mo < 10) ||
             (mo == 3 && (d > lastSunday(G.yr, 3) || (d == lastSunday(G.yr, 3) && h >= 1))) ||
             (mo == 10 && (d < lastSunday(G.yr, 10) || (d == lastSunday(G.yr, 10) && h < 1)));
  hh = (h + (bst ? 1 : 0)) % 24; mm = m;
  return true;
}

// ------------------------------------------------------------------ layout
// Rev dial (left)
static const float CX = 150, CY = 172, R1 = 124, R0 = 108;
static const float ANG0 = 135, ANG1 = 405;            // 270 degree sweep, gap at the bottom
static const float N_IN = 54, N_OUT = 127;        // needle inner/outer radius
static float rpmToAng(float rpm) { return ANG0 + (ANG1 - ANG0) * constrain(rpm, 0.0f, RPM_MAX) / RPM_MAX; }

static const Rect R_GEAR = {(int16_t)(CX - 44), (int16_t)(CY - 46), 88, 92};
static const Rect R_RPM = {(int16_t)(CX - 56), (int16_t)(CY + 72), 112, 30};
// Top bar
static const Rect R_INDL = {6, 2, 54, 38}, R_INDR = {420, 2, 54, 38};
static const Rect R_BEAM = {70, 2, 52, 38}, R_NEUT = {124, 6, 62, 30};
static const Rect R_CLOCK = {190, 2, 100, 38}, R_BRAKE = {306, 6, 90, 30};
// Bottom bar
static const Rect R_DOTS = {200, 296, 80, 20}, R_FPS = {380, 292, 96, 26};
// Ride page right side
static const Rect R_SPEED = {282, 50, 194, 102};
static const Rect R_TRIP = {340, 186, 136, 28}, R_ODO = {340, 218, 136, 28}, R_BATT = {340, 250, 136, 28};

// ------------------------------------------------------------------ static backgrounds
// Retro tricolour (red / white / blue) stripes, 80s dirt-bike tank style.
static const uint16_t C_S_RED = RGB(255, 20, 30), C_S_WHT = RGB(255, 255, 255), C_S_BLU = RGB(25, 80, 255);
static void slantBand(float x0, float y0, float x1, float thick, float slope, uint16_t c, uint8_t a) {
  // parallelogram from x0 to x1, top edge y = y0 + slope*(x - x0), 'thick' px tall
  float xs[4] = {x0, x1, x1, x0};
  float ys[4] = {y0, y0 + slope * (x1 - x0), y0 + slope * (x1 - x0) + thick, y0 + thick};
  convexPoly(xs, ys, 4, c, a);
}
static void kinkedBand(float y, float thick, float kx, float slope, uint16_t c, uint8_t a) {
  // flat from the left edge to kx, then kicks up to the top edge at 'slope'
  float xa = kx + (y - 40) * 0.2f, xb = xa + thick * 0.2f;   // corner shifts so the bands stay parallel
  float fx[4] = {-2, xa, xb, -2}, fy[4] = {y, y, y + thick, y + thick};
  convexPoly(fx, fy, 4, c, a);
  float up = (y + thick) / -slope;
  float kxs[4] = {xa, xa + y / -slope, xb + (y + thick) / -slope + 0.0f * up, xb};
  float kys[4] = {y, 0, 0, y + thick};
  kxs[2] = xb + (y + thick) / -slope;
  convexPoly(kxs, kys, 4, c, a);
}
static void retroStripes(int p) {
  // big faint diagonal sweep, low on the right
  const float SL = -0.42f;
  float y = (p == 0) ? 300 : 290;
  slantBand(230, y, 490, 16, SL, C_S_RED, STRIPE_ALPHA);
  slantBand(230, y + 21, 490, 6, SL, C_S_WHT, STRIPE_ALPHA);
  slantBand(230, y + 32, 490, 16, SL, C_S_BLU, STRIPE_ALPHA);
  // solid tricolour rule under the top bar, kicking up between BRAKE and the right arrow
  kinkedBand(40, 3, 398, -2.6f, C_S_RED, 255);
  kinkedBand(44.5f, 1.5f, 398, -2.6f, C_S_WHT, 255);
  kinkedBand(47.5f, 3, 398, -2.6f, C_S_BLU, 255);
  // thin tricolour above the bottom bar
  slantBand(-2, 287, 482, 1.5f, 0, C_S_RED, 255);
  slantBand(-2, 289.5f, 482, 1, 0, C_S_WHT, 255);
  slantBand(-2, 291.5f, 482, 1.5f, 0, C_S_BLU, 255);
}

static void renderBg(int p) {
  T = bg[p]; clipAll();
  fillRect(0, 0, W, H, C_BG);
#if RETRO_STRIPES
  retroStripes(p);
#else
  hline(0, 42, W, C_OFF);
  hline(0, 288, W, C_OFF);
#endif
#if DEMO_MODE
  text(F_SMALL, 12, 309, "DEMO", C_AMB);
  text(F_SMALL, 60, 309, "swipe for pages", C_DIM);
#else
  text(F_SMALL, 12, 309, "XL125R", C_GREY);
#endif
  if (p == 0) {
    ringSeg(CX, CY, R0, R1, ANG0, rpmToAng(RPM_SHIFT) - 0.6f, C_RING);
    ringSeg(CX, CY, R0, R1, rpmToAng(RPM_SHIFT) + 0.6f, ANG1, C_REDZ);
    for (int k = 0; k <= (int)(RPM_MAX / 500); k++) {
      float a = rpmToAng(k * 500) * DEG_TO_RAD, c = cosf(a), s = sinf(a);
      bool major = (k % 2) == 0;
      float ri = major ? R0 - 14 : R0 - 8;
      uint16_t col = (k * 500 >= RPM_SHIFT) ? C_RED : (major ? C_GREY : C_DIM);
      capsule(CX + c * (R0 - 3), CY + s * (R0 - 3), CX + c * ri, CY + s * ri, major ? 1.4f : 0.9f, col);
      if (major) {
        char n[4]; snprintf(n, sizeof n, "%d", k / 2);
        float rr = R0 - 27;
        text(F_SMALL, (int)(CX + c * rr), (int)(CY + s * rr + 5), n, (k * 500 >= RPM_SHIFT) ? C_RED : C_GREY, CENTRE);
      }
    }
    ringSeg(CX, CY, 47, 49, 0, 360, C_OFF);
    text(F_SMALL, (int)CX, (int)CY + 118, "r/min", C_DIM, CENTRE);
    text(F_SMALL, 470, 172, "MPH", C_GREY, RIGHT);
    hline(296, 180, 176, C_OFF);
    textOutlined(F_SMALL, 300, 206, "TRIP", C_GREY);
    textOutlined(F_SMALL, 300, 238, "ODO", C_GREY);
    textOutlined(F_SMALL, 300, 270, DEMO_MODE ? "BATT" : "DASH BATT", C_GREY);
  } else if (p == 1) {
    text(F_SMALL, 20, 66, "TRIP", C_AMB);
    const char *lab[6] = {"ODOMETER  mi", "TRIP A  mi", "TRIP B  mi", "AVERAGE  mph", "TOP SPEED  mph", "RIDING TIME"};
    for (int i = 0; i < 6; i++) text(F_SMALL, (i % 2) ? 256 : 20, 92 + (i / 2) * 66, lab[i], C_GREY);
    for (int y = 84; y < 280; y++) blendPx(240, y, C_OFF, 255);
  } else if (p == 3) {
    text(F_SMALL, 20, 66, "INPUT / OUTPUT TEST", C_AMB);
    textOutlined(F_SMALL, 20, 190, "Outputs (MOSFET board)", C_GREY);
  } else {
    text(F_SMALL, 20, 66, "SYSTEM", C_AMB);
    const char *lab[8] = {"Frame rate", "Draw / send", "Screen sent", "SPI clock", "PSRAM free", "Touch", "GPS", "Dash LiPo"};
    for (int i = 0; i < 8; i++) text(F_MED, 20, 98 + i * 25, lab[i], C_GREY);
  }
}
static inline void restore(const Rect &r0) {
  Rect r = rClip(r0);
  for (int y = r.y; y < r.y + r.h; y++) memcpy(T + y * W + r.x, bg[page] + y * W + r.x, r.w * 2);
}

// ------------------------------------------------------------------ icons
static bool flashOn() { return (millis() % 667) < 333; }    // ~1.5 Hz indicator flash
static bool indLit(bool left) {
#if DEMO_MODE
  return (left ? S.indL : S.indR) && flashOn();
#else
  return S.out[left ? O_IND_L : O_IND_R];
#endif
}

static void arrowIcon(const Rect &r, bool left, uint16_t c) {
  float cx = r.x + r.w / 2.0f, cy = r.y + r.h / 2.0f, s = left ? -1 : 1;
  float hx[3] = {cx + s * 20, cx + s * 2, cx + s * 2}, hy[3] = {cy, cy - 15, cy + 15};
  convexPoly(hx, hy, 3, c);
  float bx[4] = {cx + s * 4, cx - s * 18, cx - s * 18, cx + s * 4}, by[4] = {cy - 6, cy - 6, cy + 6, cy + 6};
  convexPoly(bx, by, 4, c);
}
static void beamIcon(const Rect &r, uint16_t c) {
  float cx = r.x + 30, cy = r.y + r.h / 2.0f;
  ringSeg(cx, cy, 0, 11, 90, 270, c);
  fillRect((int)cx, (int)cy - 11, 3, 22, c);
  for (int i = -1; i <= 1; i++) capsule(cx - 15, cy + i * 7, cx - 27, cy + i * 7, 1.5f, c);
}

// ------------------------------------------------------------------ widgets
static uint32_t fnv(const char *s, uint32_t h = 2166136261u) { for (; *s; s++) h = (h ^ (uint8_t)*s) * 16777619u; return h; }

enum WId { W_INDL, W_INDR, W_BEAM, W_NEUT, W_CLOCK, W_BRAKE, W_DOTS, W_FPS,
           W_SPEED, W_TRIP, W_ODO, W_BATT,
           W_T0, W_T1, W_T2, W_T3, W_T4, W_T5, W_SYS, W_BTNS, W_OUTS, W_TINFO, W_COUNT };
static uint32_t lastKey[W_COUNT];
static const int8_t WPAGE[W_COUNT] = {-1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 3, 3, 3};

static Rect tripRect(int i) { return Rect{(int16_t)((i % 2) ? 252 : 16), (int16_t)(100 + (i / 2) * 66), 220, 42}; }
static Rect widgetRect(int id) {
  switch (id) {
    case W_INDL: return R_INDL; case W_INDR: return R_INDR; case W_BEAM: return R_BEAM;
    case W_NEUT: return R_NEUT; case W_CLOCK: return R_CLOCK; case W_BRAKE: return R_BRAKE;
    case W_DOTS: return R_DOTS; case W_FPS: return R_FPS; case W_SPEED: return R_SPEED;
    case W_TRIP: return R_TRIP; case W_ODO: return R_ODO; case W_BATT: return R_BATT;
    case W_SYS: return Rect{180, 76, 296, 206};
    case W_BTNS: return Rect{14, 74, 452, 96};
    case W_OUTS: return Rect{14, 196, 452, 56};
    case W_TINFO: return Rect{14, 254, 452, 40};
    default: return tripRect(id - W_T0);
  }
}

static void fmtHMS(char *b, size_t n, float s) { int t = (int)s; snprintf(b, n, "%d:%02d:%02d", t / 3600, (t / 60) % 60, t % 60); }
static int shownMph() { return (int)(showMph + 0.5f); }

static void sysLines(char out[8][32]) {
  snprintf(out[0], 32, "%d fps", fps);
  snprintf(out[1], 32, "%.1f / %.1f ms", drawMs, sendMs);
  snprintf(out[2], 32, "%.0f%% per frame", sentPct);
  snprintf(out[3], 32, "%d MHz", SPI_HZ / 1000000);
  snprintf(out[4], 32, "%.1f MB", heap_caps_get_free_size(MALLOC_CAP_SPIRAM) / 1048576.0f);
  if (!touchOk) snprintf(out[5], 32, "not found");
  else if (touchX < 0) snprintf(out[5], 32, "-");
  else snprintf(out[5], 32, "x %d  y %d", touchX, touchY);
#if GPS_RX_PIN >= 0
  if (!G.seen || millis() - G.lastMs > 3000) snprintf(out[6], 32, "no data (pin %d)", GPS_RX_PIN);
  else snprintf(out[6], 32, "%s, %d sats", G.fix ? "fix" : "no fix", G.sats);
#else
  snprintf(out[6], 32, "off");
#endif
  if (S.lipoPct >= 0) snprintf(out[7], 32, "%.2f V %d%%%s", S.lipoV, S.lipoPct, S.charging ? " chg" : "");
  else snprintf(out[7], 32, "%s", S.supplyOn ? "no battery" : "?");
}

// Key = everything the widget shows. Redrawn only when it changes.
static uint32_t widgetKey(int id) {
  char b[64];
  switch (id) {
    case W_INDL: return indLit(true) ? 1 : 2;
    case W_INDR: return indLit(false) ? 1 : 2;
    case W_BEAM: return S.beam ? 1 : (S.lightsOn ? 2 : 3);
    case W_NEUT: return S.horn ? 1 : 2;
    case W_BRAKE: return S.brake ? 1 : 2;
    case W_CLOCK: { int hh, mm; return ukClock(hh, mm) ? (uint32_t)(hh * 60 + mm + 10) : 1; }
    case W_DOTS: return page + 11;
    case W_FPS: return fps + 1000;
    case W_SPEED: return shownMph() * 2 + (gpsLive() ? 1 : 0) + 100;
    case W_TRIP: snprintf(b, sizeof b, "%.1f", S.tripA); return fnv(b);
    case W_ODO: snprintf(b, sizeof b, "%.1f", S.odo); return fnv(b);
    case W_BATT: snprintf(b, sizeof b, "%.1f %d %d", S.battV, S.lipoPct, S.charging); return fnv(b);
    case W_BTNS: {
      uint32_t k = (uint32_t)S.btn * 4 + (S.mcpAddr < 0 ? 0 : S.mcpAddr) * 1024 + eventCount * 262144u + 1;
      const Button *bs[5] = {&bL, &bR, &bHorn, &bLights, &bMode};
      for (int i = 0; i < 5; i++) if (bs[i]->down) k = k * 31 + (millis() - bs[i]->downMs) / 100;   // held time, 0.1 s steps
      return k;
    }
    case W_OUTS: { uint32_t k = 1; for (int i = 0; i < 8; i++) k = k * 2 + (S.out[i] ? 1 : 0); return k; }
    case W_TINFO: snprintf(b, sizeof b, "%d%d%d%d%d%d%d%d%d", S.brake, (int)S.rpm / 10, (int)(S.mph * 10), G.sats,
                           S.lightsOn, S.high, S.flash, S.hazard, S.horn * 2 + S.drl); return fnv(b);
    case W_SYS: { if (millis() % 500 > 40) return lastKey[W_SYS]; char l[8][32]; sysLines(l); uint32_t h = 2166136261u; for (int i = 0; i < 8; i++) h = fnv(l[i], h); return h; }
    default: {
      int i = id - W_T0;
      if (i == 0) snprintf(b, sizeof b, "%.1f", S.odo);
      else if (i == 1) snprintf(b, sizeof b, "%.2f", S.tripA);
      else if (i == 2) snprintf(b, sizeof b, "%.1f", S.tripB);
      else if (i == 3) snprintf(b, sizeof b, "%.1f", S.movingS > 1 ? S.tripA / (S.movingS / 3600.0) : 0.0);
      else if (i == 4) snprintf(b, sizeof b, "%.1f", S.maxMph);
      else fmtHMS(b, sizeof b, S.rideS);
      return fnv(b);
    }
  }
}

static void drawWidget(int id) {
  Rect r = widgetRect(id);
  char b[64];
  switch (id) {
    case W_INDL: arrowIcon(r, true, indLit(true) ? C_GRN : C_OFF); break;
    case W_INDR: arrowIcon(r, false, indLit(false) ? C_GRN : C_OFF); break;
    case W_BEAM: beamIcon(r, S.beam ? C_BLU : (S.lightsOn ? C_GRN : C_OFF)); break;   // blue high, green low, grey off
    case W_NEUT:   // HORN light
      if (S.horn) { capsule(r.x + 15, r.y + 15, r.x + r.w - 15, r.y + 15, 14, C_AMB); text(F_SMALL, r.x + r.w / 2, r.y + 20, "HORN", C_BG, CENTRE); }
      else text(F_SMALL, r.x + r.w / 2, r.y + 20, "HORN", C_OFF, CENTRE);
      break;
    case W_BRAKE:
      if (S.brake) { capsule(r.x + 15, r.y + 15, r.x + r.w - 15, r.y + 15, 14, C_RED); text(F_MED, r.x + r.w / 2, r.y + 24, "BRAKE", C_TXT, CENTRE); }
      else text(F_MED, r.x + r.w / 2, r.y + 24, "BRAKE", C_OFF, CENTRE);
      break;
    case W_CLOCK: {
      int hh, mm;
      if (ukClock(hh, mm)) snprintf(b, sizeof b, "%02d:%02d", hh, mm); else snprintf(b, sizeof b, "--:--");
      text(F_MED, r.x + r.w / 2, r.y + 29, b, C_TXT, CENTRE);
      break;
    }
    case W_DOTS:
      for (int i = 0; i < NPAGES; i++) disc(r.x + 16 + i * 16, r.y + 10, i == page ? 4.5f : 3.0f, i == page ? C_TXT : C_DIM);
      break;
    case W_FPS: snprintf(b, sizeof b, "%d fps", fps); textOutlined(F_SMALL, r.x + r.w - 6, r.y + 17, b, C_DIM, RIGHT); break;
    case W_SPEED: {
      snprintf(b, sizeof b, "%d", shownMph());
      text(F_SPEED, 470, 140, b, C_TXT, RIGHT);
      if (gpsLive()) text(F_SMALL, 300, 172, "GPS", C_GRN);
      break;
    }
    case W_TRIP: snprintf(b, sizeof b, "%.1f", S.tripA); textOutlined(F_MED, 470, r.y + 21, b, C_TXT, RIGHT); break;
    case W_ODO: snprintf(b, sizeof b, "%.1f", S.odo); textOutlined(F_MED, 470, r.y + 21, b, C_TXT, RIGHT); break;
    case W_BATT:
#if DEMO_MODE
      snprintf(b, sizeof b, "%.1f V", S.battV); textOutlined(F_MED, 470, r.y + 21, b, S.battV > 13 ? C_GRN : C_AMB, RIGHT);
#else
      if (S.lipoPct >= 0) snprintf(b, sizeof b, "%s%d%%", S.charging ? "+" : "", S.lipoPct); else snprintf(b, sizeof b, "--");
      textOutlined(F_MED, 470, r.y + 21, b, S.lipoPct > 30 || S.lipoPct < 0 ? C_GRN : C_AMB, RIGHT);
#endif
      break;
    case W_BTNS: {
      static const char *nm[5] = {"IND L", "IND R", "HORN", "LIGHTS", "MODE"};
      static const int pins[5] = {BTN_IND_L, BTN_IND_R, BTN_HORN, BTN_LIGHTS, BTN_MODE};
      const Button *bs[5] = {&bL, &bR, &bHorn, &bLights, &bMode};
      for (int i = 0; i < 5; i++) {
        bool on = S.btn & (1 << pins[i]);
        int x = r.x + 6 + i * 89;
        capsule(x + 14, r.y + 26, x + 66, r.y + 26, 18, on ? C_GRN : C_OFF);
        text(F_SMALL, x + 40, r.y + 31, nm[i], on ? C_BG : C_GREY, CENTRE);
        if (bs[i]->down) {             // how long it's been held: amber once it counts as a hold
          uint32_t ms = millis() - bs[i]->downMs;
          snprintf(b, sizeof b, "%.1f s", ms / 1000.0f);
          text(F_SMALL, x + 40, r.y + 60, b, ms >= 3000 ? C_RED : ms >= HOLD_MS ? C_AMB : C_TXT, CENTRE);
        } else {
          snprintf(b, sizeof b, "PA%d", pins[i]);
          text(F_SMALL, x + 40, r.y + 60, b, C_DIM, CENTRE);
        }
      }
      if (S.mcpAddr >= 0) snprintf(b, sizeof b, "Chip 0x%02X", S.mcpAddr);
      else snprintf(b, sizeof b, "Chip NOT FOUND");
      textOutlined(F_SMALL, r.x + 6, r.y + 84, b, S.mcpAddr >= 0 ? C_GRN : C_RED);
      textOutlined(F_SMALL, r.x + 112, r.y + 84, "Last:", C_GREY);
      textOutlined(F_SMALL, r.x + 156, r.y + 84, lastEvent, C_AMB);
      break;
    }
    case W_OUTS:
      for (int i = 0; i < 8; i++) {
        int x = r.x + 4 + i * 56;
        capsule(x + 12, r.y + 18, x + 38, r.y + 18, 14, S.out[i] ? C_AMB : C_OFF);
        snprintf(b, sizeof b, "%d", i + 1);
        text(F_SMALL, x + 25, r.y + 23, b, S.out[i] ? C_BG : C_GREY, CENTRE);
        textOutlined(F_SMALL, x + 25, r.y + 50, OUT_NAME[i], C_GREY, CENTRE);
      }
      break;
    case W_TINFO:
      snprintf(b, sizeof b, "Head: %s  Beam: %s%s  DRL: %s  Haz: %s  Horn: %s", S.lightsOn ? "ON" : "OFF",
               S.high && S.lightsOn ? "HIGH" : S.lightsOn ? "low" : "-", S.flash ? "+FLASH" : "",
               !S.drl ? "off" : S.lightsOn ? "dim" : "FULL", S.hazard ? "ON" : "off", S.horn ? "ON" : "off");
      textOutlined(F_SMALL, r.x + 6, r.y + 16, b, C_TXT);
      snprintf(b, sizeof b, "Brake: %s    RPM in: %d    GPS: %.1f mph, %d sats", S.brake ? "ON" : "off", (int)S.rpm, S.mph, G.sats);
      textOutlined(F_SMALL, r.x + 6, r.y + 35, b, C_TXT);
      break;
    case W_SYS: { char l[8][32]; sysLines(l); for (int i = 0; i < 8; i++) text(F_MED, 470, 98 + i * 25, l[i], C_TXT, RIGHT); break; }
    default: {
      int i = id - W_T0;
      if (i == 0) snprintf(b, sizeof b, "%.1f", S.odo);
      else if (i == 1) snprintf(b, sizeof b, "%.2f", S.tripA);
      else if (i == 2) snprintf(b, sizeof b, "%.1f", S.tripB);
      else if (i == 3) snprintf(b, sizeof b, "%.1f", S.movingS > 1 ? S.tripA / (S.movingS / 3600.0) : 0.0);
      else if (i == 4) snprintf(b, sizeof b, "%.1f", S.maxMph);
      else fmtHMS(b, sizeof b, S.rideS);
      text(F_BIG, r.x + 4, r.y + 34, b, C_TXT);
    }
  }
}

static void updateWidgets(bool force) {
  for (int id = 0; id < W_COUNT; id++) {
    if (WPAGE[id] >= 0 && WPAGE[id] != page) continue;
    uint32_t k = widgetKey(id);
    if (!force && k == lastKey[id]) continue;
    lastKey[id] = k;
    Rect r = widgetRect(id);
    restore(r);
    setClip(r);
    drawWidget(id);
    clipAll();
    addDirty(r);
  }
}

// ------------------------------------------------------------------ the rev dial
static float ghost[3] = {ANG0, ANG0, ANG0};
static Rect prevNeedleBox = {0, 0, 0, 0};
static float prevLit = ANG0;
static int prevArcCol = -1;
static uint32_t prevGearKey = 0, prevRpmKey = 0;

static void needleQuad(float angDeg, float *xs, float *ys) {
  float a = angDeg * DEG_TO_RAD, c = cosf(a), s = sinf(a);
  float w0 = 4.5f, w1 = 1.4f;
  xs[0] = CX + c * N_IN - s * w0;  ys[0] = CY + s * N_IN + c * w0;
  xs[1] = CX + c * N_OUT - s * w1; ys[1] = CY + s * N_OUT + c * w1;
  xs[2] = CX + c * N_OUT + s * w1; ys[2] = CY + s * N_OUT - c * w1;
  xs[3] = CX + c * N_IN + s * w0;  ys[3] = CY + s * N_IN - c * w0;
}
static Rect needleBox(float ang) {
  float xs[4], ys[4];
  needleQuad(ang, xs, ys);
  float x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (int i = 0; i < 4; i++) { x0 = min(x0, xs[i]); x1 = max(x1, xs[i]); y0 = min(y0, ys[i]); y1 = max(y1, ys[i]); }
  return Rect{(int16_t)(x0 - 3), (int16_t)(y0 - 3), (int16_t)(x1 - x0 + 7), (int16_t)(y1 - y0 + 7)};
}
static int arcColourIdx(float rpm) {
  if (rpm >= RPM_SHIFT) return ((millis() / 90) % 2) ? 3 : 2;   // flashing shift light
  return rpm >= RPM_AMBER ? 1 : 0;
}
static const uint16_t ARC_COL[4] = {C_COOL, C_AMB, C_RED, C_TXT};
static const uint8_t GHOST_A[3] = {110, 60, 28};

static void drawDialContents(float needleAng, int arcCol) {
  if (needleAng > ANG0 + 0.2f) ringSeg(CX, CY, R0, R1, ANG0, needleAng, ARC_COL[arcCol]);
#if GHOST_TRAIL
  for (int i = 2; i >= 0; i--) {
    if (fabsf(ghost[i] - needleAng) < 0.6f) continue;
    float xs[4], ys[4]; needleQuad(ghost[i], xs, ys); convexPoly(xs, ys, 4, C_NEEDLE, GHOST_A[i]);
  }
#endif
  float xs[4], ys[4];
  needleQuad(needleAng, xs, ys);
  convexPoly(xs, ys, 4, C_NEEDLE);
  char b[16];
  if (S.gear == 0) text(F_GEAR, (int)CX, (int)CY + 31, DEMO_MODE ? "N" : "-", DEMO_MODE ? C_GRN : C_DIM, CENTRE);
  else { snprintf(b, sizeof b, "%d", S.gear); text(F_GEAR, (int)CX, (int)CY + 31, b, C_TXT, CENTRE); }
  snprintf(b, sizeof b, "%d", ((int)(showRpm + 25) / 50) * 50);
  text(F_MED, (int)CX, (int)CY + 96, b, C_TXT, CENTRE);
}

static void updateDial(bool force) {
  if (page != 0) return;
  float ang = rpmToAng(showRpm);
  int col = arcColourIdx(showRpm);
  uint32_t gearKey = S.gear + 1, rpmKey = ((int)(showRpm + 25) / 50) + 1;
  bool ghostsVisible = false;
#if GHOST_TRAIL
  for (int i = 0; i < 3; i++) if (fabsf(ghost[i] - ang) >= 0.6f) ghostsVisible = true;
#endif
  bool moved = fabsf(ang - prevLit) > 0.03f;
  Rect rs[3]; int n = 0;
  if (force) {
    rs[n++] = rUnion(arcBox(CX, CY, R0, R1, ANG0, ANG1), rUnion(R_GEAR, R_RPM));
  } else {
    if (moved || ghostsVisible || col != prevArcCol) {
      Rect box = needleBox(ang);
#if GHOST_TRAIL
      for (int i = 0; i < 3; i++) box = rUnion(box, needleBox(ghost[i]));
#endif
      Rect r = rUnion(box, prevNeedleBox);
      if (col != prevArcCol) r = rUnion(r, arcBox(CX, CY, R0, R1, ANG0, max(ang, prevLit)));
      else r = rUnion(r, arcBox(CX, CY, R0, R1, min(ang, prevLit), max(ang, prevLit)));
      rs[n++] = r;
    }
    if (gearKey != prevGearKey) rs[n++] = R_GEAR;
    if (rpmKey != prevRpmKey) rs[n++] = R_RPM;
  }
  for (int i = 0; i < n; i++) {
    restore(rs[i]);
    setClip(rs[i]);
    drawDialContents(ang, col);
    clipAll();
    addDirty(rs[i]);
  }
  Rect box = needleBox(ang);
#if GHOST_TRAIL
  for (int i = 0; i < 3; i++) box = rUnion(box, needleBox(ghost[i]));
  if (n || force) { ghost[2] = ghost[1]; ghost[1] = ghost[0]; ghost[0] = ang; }
#endif
  prevNeedleBox = box;
  prevLit = ang; prevArcCol = col; prevGearKey = gearKey; prevRpmKey = rpmKey;
}

// ------------------------------------------------------------------ page change (slide)
static void renderPageInto(uint16_t *buf) {
  T = buf;
  memcpy(buf, bg[page], W * H * 2);
  collectDirty = false;
  updateWidgets(true);
  updateDial(true);
  collectDirty = true;
  T = fb;
}
static float easeOutCubic(float t) { t = 1 - t; return 1 - t * t * t; }

static void changePage(int dir) {
  int newPage = (page + dir + NPAGES) % NPAGES;
  memcpy(oldBuf, fb, W * H * 2);
  page = newPage;
  prevNeedleBox = Rect{0, 0, 0, 0};
  renderPageInto(pageBuf);
  // top + bottom bars change in place, the middle slides
  const int Y0 = 43, Y1 = 288;
  memcpy(fb, pageBuf, Y0 * W * 2);
  memcpy(fb + Y1 * W, pageBuf + Y1 * W, (H - Y1) * W * 2);
  sendRect(Rect{0, 0, W, Y0});
  sendRect(Rect{0, Y1, W, H - Y1});
  uint32_t t0 = millis();
  const float DUR = 280;
  while (true) {
    float t = min(1.0f, (millis() - t0) / DUR);
    int off = (int)(easeOutCubic(t) * W + 0.5f);
    for (int y = Y0; y < Y1; y++) {
      uint16_t *d = fb + y * W, *o = oldBuf + y * W, *nw = pageBuf + y * W;
      if (dir > 0) { memcpy(d, o + off, (W - off) * 2); memcpy(d + W - off, nw, off * 2); }
      else { memcpy(d + off, o, (W - off) * 2); memcpy(d, nw + W - off, off * 2); }
    }
    sendRect(Rect{0, Y0, W, Y1 - Y0});
    if (t >= 1) break;
    yield();
  }
  memcpy(fb, pageBuf, W * H * 2);
  nDirty = 0;
}

// ------------------------------------------------------------------ touch (FT6336 at 0x38)
static bool readTouch(int16_t &x, int16_t &y) {
  Wire.beginTransmission(TOUCH_ADDR);
  Wire.write(0x02);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((uint8_t)TOUCH_ADDR, (uint8_t)5) != 5) return false;
  uint8_t b[5];
  for (int i = 0; i < 5; i++) b[i] = Wire.read();
  int n = b[0] & 0x0F;
  if (n == 0 || n > 2) return false;
  int nx = ((b[1] & 0x0F) << 8) | b[2], ny = ((b[3] & 0x0F) << 8) | b[4];
  int sx = TOUCH_SWAP_XY ? ny : nx, sy = TOUCH_SWAP_XY ? nx : ny;
  if (TOUCH_FLIP_X) sx = W - 1 - sx;
  if (TOUCH_FLIP_Y) sy = H - 1 - sy;
  x = sx; y = sy;
  return true;
}

static bool tDown = false;
static int16_t tx0, ty0;
static uint32_t tT0, lastTouchPoll = 0, lastAutoPage = 0;

static int pollGesture() {   // returns -1 / +1 for a page change, 0 for none
  if (!touchOk || millis() - lastTouchPoll < 15) return 0;
  lastTouchPoll = millis();
  int16_t x, y;
  bool d = readTouch(x, y);
  if (d) {
    touchX = x; touchY = y;
    if (!tDown) { tDown = true; tx0 = x; ty0 = y; tT0 = millis(); Serial.printf("touch down x=%d y=%d\n", x, y); }
    return 0;
  }
  if (!tDown) return 0;
  tDown = false;
  int dx = touchX - tx0, dy = touchY - ty0;
  Serial.printf("touch up   x=%d y=%d (dx %d dy %d)\n", touchX, touchY, dx, dy);
  if (abs(dx) > 50 && abs(dx) > abs(dy)) return dx < 0 ? +1 : -1;   // swipe left = next page
  if (abs(dx) < 20 && abs(dy) < 20 && millis() - tT0 < 400) return +1;  // tap = next page
  return 0;
}

// ------------------------------------------------------------------ setup / loop
static void fail(const char *msg) {
  Serial.println(msg);
  lcd->fillScreen(0x0000);
  lcd->setTextColor(0xFFFF);
  lcd->setTextSize(2);
  lcd->setCursor(10, 10);
  lcd->println(msg);
  while (true) delay(1000);
}

static void *psram(size_t n) { return heap_caps_malloc(n, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT); }

static uint32_t lastMs = 0, fpsT0 = 0, framesSent = 0, drawUs = 0, sendUs = 0;

void dashSetup() {
  Serial.begin(115200);
  // outputs first, all off, so nothing twitches while the screen starts
  for (int i = 0; i < 8; i++) if (PIN_OUT[i] >= 0) { pinMode(PIN_OUT[i], OUTPUT); digitalWrite(PIN_OUT[i], OUT_ACTIVE_HIGH ? LOW : HIGH); }
  if (PIN_OUT[O_TAIL] >= 0) ledcAttach(PIN_OUT[O_TAIL], TAIL_PWM_HZ, 8);   // esp32 core 3.x API
  if (PIN_OUT[O_AUX] >= 0) ledcAttach(PIN_OUT[O_AUX], TAIL_PWM_HZ, 8);     // DRL dimming
  pinMode(PIN_BRAKE, INPUT_PULLUP);
  pinMode(PIN_RPM, INPUT_PULLDOWN);              // stays quiet with nothing plugged in
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), rpmISR, RISING);
  prefs.begin("xl", false);
  S.odo = prefs.getDouble("odo", 0); S.tripA = prefs.getDouble("tripA", 0); S.tripB = prefs.getDouble("tripB", 0);
  lastSavedOdo = S.odo;

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(I2C_HZ);
  TCA.begin();
  TCA.pinMode1(1, OUTPUT);
  TCA.write1(1, 1); delay(10); TCA.write1(1, 0); delay(10); TCA.write1(1, 1); delay(200);   // screen reset

  if (!lcd->begin(SPI_HZ)) Serial.println("lcd->begin() failed");
  lcd->fillScreen(0x0000);
  pinMode(PIN_BL, OUTPUT);
  digitalWrite(PIN_BL, HIGH);

  fb = (uint16_t *)psram(W * H * 2);
  for (int i = 0; i < NPAGES; i++) bg[i] = (uint16_t *)psram(W * H * 2);
  oldBuf = (uint16_t *)psram(W * H * 2);
  pageBuf = (uint16_t *)psram(W * H * 2);
  xfer = (uint16_t *)heap_caps_malloc(XFER_PIX * 2, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
  if (!fb || !bg[0] || !bg[1] || !bg[2] || !bg[3] || !oldBuf || !pageBuf)
    fail("No PSRAM. Tools > PSRAM > OPI PSRAM, then upload again.");
  if (!xfer) fail("Out of memory (xfer buffer)");

  Wire.beginTransmission(TOUCH_ADDR);
  touchOk = Wire.endTransmission() == 0;
  Serial.printf("Touch %s\n", touchOk ? "found" : "NOT found: pages change by themselves every 10 s");
  mcpFind();
#if DEMO_MODE
  phase = BOOT_SWEEP;
#else
  phase = STOPPED;
#endif

#if GPS_RX_PIN >= 0
  Serial1.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
#endif

  for (int p = 0; p < NPAGES; p++) renderBg(p);
  bootMs = millis();
  renderPageInto(fb);
  sendRect(Rect{0, 0, W, H});
  lastMs = fpsT0 = lastAutoPage = millis();
  Serial.println(DEMO_MODE ? "XL dash v1 running (DEMO_MODE 1)" : "XL dash v1 running");
}

void dashLoop() {
  uint32_t now = millis();
  float dt = min(0.1f, (now - lastMs) / 1000.0f);
  lastMs = now;

  pollGps();
  handleButtons();
#if !DEMO_MODE
  writeOutputs();
#endif
  int g = pollGesture();
  if (pendingPage) { g = pendingPage; pendingPage = 0; }
  if (!touchOk && now - lastAutoPage > 10000) { g = +1; lastAutoPage = now; }
  if (g) { changePage(g); lastMs = millis(); return; }

#if DEMO_MODE
  simulate(dt);
  float targetMph = gpsLive() ? G.mph : S.mph;
#else
  realUpdate(dt);
  float targetMph = S.mph;
#endif
  showRpm = smoothDamp(showRpm, S.rpm, rpmVel, NEEDLE_EASE_S, dt);
  showMph = smoothDamp(showMph, targetMph, mphVel, SPEED_EASE_S, dt);

  uint32_t t0 = micros();
  T = fb;
  updateDial(false);
  updateWidgets(false);
  uint32_t t1 = micros();
  bool any = nDirty > 0;
  flushDirty();
  uint32_t t2 = micros();
  if (any) { framesSent++; drawUs += t1 - t0; sendUs += t2 - t1; }

  if (now - fpsT0 >= 1000) {
    fps = framesSent;
    drawMs = framesSent ? drawUs / 1000.0f / framesSent : 0;
    sendMs = framesSent ? sendUs / 1000.0f / framesSent : 0;
    sentPct = framesSent ? 100.0f * statPx / framesSent / (W * H) : 0;
    framesSent = 0; drawUs = sendUs = 0; statPx = 0; fpsT0 = now;
  }
  if (!any) delay(1);
}
