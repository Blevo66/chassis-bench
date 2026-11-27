// Host preview: runs the demo with a fake clock and screen, saves PPM frames.
// Screen alone (no brain box: test page shows NO BOX). Button tests: link-test.cpp
// g++ -std=gnu++17 -O2 -Ifake -I../.. preview.cpp -o preview && ./preview out/
#include "fake/Arduino.h"
uint64_t g_us = 0; double g_spi_hz = 40e6; uint16_t g_screen[480 * 320];
FakeSerial Serial, Serial1, Serial2;
#include "fake/Wire.h"
FakeWire Wire;
uint8_t g_fake_btns = 0;
#include "../../config.h"
#include "../../dash.h"
static void save(const char *dir, const char *name) {
  char p[256]; snprintf(p, sizeof p, "%s/%s.ppm", dir, name);
  FILE *f = fopen(p, "wb"); fprintf(f, "P6 480 320 255\n");
  for (auto c : g_screen) { uint8_t rgb[3] = {(uint8_t)((c >> 11) << 3), (uint8_t)(((c >> 5) & 63) << 2), (uint8_t)((c & 31) << 3)}; fwrite(rgb, 1, 3, f); }
  fclose(f);
}
int main(int argc, char **argv) {
  const char *dir = argc > 1 ? argv[1] : ".";
  dashSetup();
  double shots[] = {0.4, 3.0, 6.3, 9.0, 12.5, 16.0, 19.0, 24.0};
  int si = 0;
  while (si < 8) {
    dashLoop();
    g_us += 2500;   // pretend drawing takes ~2.5 ms on the ESP32 (guess)
    if (millis() / 1000.0 >= shots[si]) { char n[32]; snprintf(n, sizeof n, "ride-%02d", si); save(dir, n); fprintf(stderr, "t=%.1f fps=%d send=%.1fms sent=%.0f%% rpm=%.0f gear=%d\n", shots[si], fps, sendMs, sentPct, showRpm, S.gear); si++; }
  }
  while (page != 3) changePage(+1);
  for (int i = 0; i < 300; i++) { dashLoop(); g_us += 2500; } save(dir, "test");
  return 0;
}
