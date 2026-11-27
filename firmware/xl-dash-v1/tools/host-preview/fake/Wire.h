#pragma once
#include <Arduino.h>
// Fake bus: an MCP23017 at 0x27 (buttons from g_fake_btns) and a PCA9685 at 0x40
// (channel writes decoded into g_pca[0..7] as 0..4095). Nothing else answers.
extern uint8_t g_fake_btns;
extern int g_pca[8];
struct FakeWire {
  uint8_t addr = 0, reg = 0, buf[8]; int n = 0;
  void begin(int, int) {} void setClock(uint32_t) {}
  void beginTransmission(uint8_t a) { addr = a; n = 0; }
  size_t write(uint8_t v) { if (n == 0) reg = v; if (n < 8) buf[n] = v; n++; return 1; }
  uint8_t endTransmission(bool = true) {
    if (addr == 0x40 && n == 5 && reg >= 6 && reg < 6 + 32) {
      int ch = (reg - 6) / 4; uint16_t on = buf[1] | buf[2] << 8, off = buf[3] | buf[4] << 8;
      if (ch < 8) g_pca[ch] = (on & 0x1000) ? 4095 : (off & 0x1000) ? 0 : off;
    }
    return (addr == 0x27 || addr == 0x40) ? 0 : 2;
  }
  uint8_t requestFrom(uint8_t a, uint8_t k) { return a == 0x27 ? k : 0; }
  int read() { if (reg == 0x12) return (uint8_t)~g_fake_btns; return 0xFF; }
};
extern FakeWire Wire;
