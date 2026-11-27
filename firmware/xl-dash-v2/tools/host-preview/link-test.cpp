// Runs the BRAIN BOX firmware and the SCREEN firmware together on the PC, joined by a fake
// serial wire, presses buttons on a fake left controller and checks what both sides do.
// g++ -std=gnu++17 -O2 -Ifake -I../.. link-test.cpp -o link-test && ./link-test out/
#include "fake/Arduino.h"
uint64_t g_us = 0; double g_spi_hz = 40e6; uint16_t g_screen[480 * 320];
FakeSerial Serial, Serial1, Serial2, BoxLink, ScreenLink;
#include "fake/Wire.h"
FakeWire Wire;
uint8_t g_fake_btns = 0;
#include <Preferences.h>
#include <esp_heap_caps.h>
#include <Arduino_GFX_Library.h>
#include "TCA9554.h"

#define LINK_SERIAL BoxLink
namespace box {
#include "../../../xl-brain/brain_config.h"
#include "../../../xl-brain/brain.h"
}
#undef LINK_SERIAL
#undef PIN_SDA
#undef PIN_SCL
#undef LINK_RX_PIN
#undef LINK_TX_PIN
#undef LINK_BAUD
#undef I2C_HZ
#undef BTN_IND_L
#undef BTN_IND_R
#undef BTN_HORN
#undef BTN_LIGHTS
#undef BTN_MODE
#define LINK_SERIAL ScreenLink
namespace scr {
#include "../../config.h"
#include "../../dash.h"
}

static int fails = 0;
static void check(bool ok, const char *what) { fprintf(stderr, "%s  %s\n", ok ? "ok  " : "FAIL", what); if (!ok) fails++; }
static void run(uint8_t btns, double s) {        // both loops, ~1 ms per box pass, screen every 5th
  g_fake_btns = btns;
  for (int i = 0; i < s * 1000; i++) {
    box::brainLoop(); g_us += 1000;
    if (i % 5 == 0) { scr::lastAutoPage = millis(); scr::dashLoop(); }
  }
}
static void save(const char *dir, const char *name) {
  char p[256]; snprintf(p, sizeof p, "%s/%s.ppm", dir, name);
  FILE *f = fopen(p, "wb"); fprintf(f, "P6 480 320 255\n");
  for (auto c : g_screen) { uint8_t r = (c >> 11) << 3, g = ((c >> 5) & 63) << 2, b = (c & 31) << 3; fputc(r, f); fputc(g, f); fputc(b, f); }
  fclose(f);
}
int main(int argc, char **argv) {
  const char *dir = argc > 1 ? argv[1] : ".";
  BoxLink.peer = &ScreenLink; ScreenLink.peer = &BoxLink;
  box::brainSetup();
  scr::dashSetup();
  run(0, 1.0);
  check(scr::linkOk(), "screen hears the box");
  check(box::B.screenPage == 0, "box hears the screen's page");
  check(box::B.out[box::O_DRL] && box::B.out[box::O_TAIL] && !box::B.out[box::O_LOW], "boot: DRL + tail on, headlight off");
  check(scr::S.out[box::O_DRL] && !scr::S.lightsOn, "screen shows the same");

  run(0x01, 0.1); run(0, 0.3);
  check(box::B.indL && scr::S.indL, "IND L tap: left indicator on (box + screen)");
  run(0x01, 0.1); run(0, 0.3);
  check(!box::B.indL, "IND L tap again: off");
  run(0x02, 1.0); run(0, 0.3);
  check(box::B.hazard && scr::S.hazard, "IND R hold: hazards on");
  run(0x02, 1.0); run(0, 0.3);
  check(!box::B.hazard, "IND R hold again: hazards off");

  run(0x08, 0.1); run(0, 0.3);
  check(!box::B.lightsOn && !box::B.high, "LIGHTS tap with headlight off: nothing");
  run(0x08, 3.2); run(0, 0.3);
  check(box::B.lightsOn && box::B.out[box::O_LOW] && !box::B.out[box::O_HIGH], "LIGHTS hold 3 s: low beam on");
  run(0x08, 0.1); run(0, 0.3);
  check(box::B.high && box::B.out[box::O_HIGH] && scr::S.beam, "LIGHTS tap: high beam (screen beam icon too)");

  run(0x04, 0.2);
  check(box::B.out[box::O_HORN] && scr::S.horn, "HORN held: horn output on");
  run(0, 0.2);
  check(!box::B.out[box::O_HORN], "HORN released: off");

  run(0x10, 0.1);
  run(0, 0.05);
  check(box::B.flash, "MODE tap: high beam flash");

  int p0 = scr::page;
  run(0x10, 1.0); run(0, 1.0);
  check(scr::page == (p0 + 1) % 4, "MODE hold: screen goes to next page");
  check(scr::page == 1 && box::B.screenPage == 1, "now on TRIP page, box knows");
  scr::S.tripA = 12.3;
  run(0x10, 3.3); run(0, 1.0);
  check(scr::S.tripA == 0 && scr::page == 1, "TRIP page, MODE hold 3 s: trip A reset, stays on TRIP");
  run(0x10, 1.0); run(0, 1.0);
  check(scr::page == 2, "TRIP page, MODE hold 1 s: next page");
  run(0x10, 1.0); run(0, 1.0);
  check(scr::page == 3, "on TEST page");
  run(0x08, 1.2);   // (screen passes add time too, so keep this well under 3 s)
  save(dir, "link-test-page");
  run(0, 0.5);

  BoxLink.peer = ScreenLink.peer = nullptr; BoxLink.echo = ScreenLink.echo = false;   // pull the plug
  run(0, 1.5);
  check(!scr::linkOk(), "cable pulled: screen notices");
  check(box::B.screenPage == -1 && box::B.out[box::O_DRL] && box::B.out[box::O_LOW], "cable pulled: box carries on, lights stay on");
  run(0x01, 0.1); run(0, 0.3);
  check(box::B.indL, "cable pulled: buttons still work on the box");
  save(dir, "link-test-nobox");
  fprintf(stderr, "\n%d failed\n", fails);
  return fails ? 1 : 0;
}
