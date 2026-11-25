#pragma once
#include <Arduino.h>
// Fake bus: an MCP23017 at 0x27 with IND L (PA0) and HORN (PA2) held down; nothing else answers.
extern uint8_t g_fake_btns;
struct FakeWire {
  uint8_t addr = 0, reg = 0; int n = 0;
  void begin(int, int) {} void setClock(uint32_t) {}
  void beginTransmission(uint8_t a) { addr = a; n = 0; }
  size_t write(uint8_t v) { if (n++ == 0) reg = v; return 1; }
  uint8_t endTransmission(bool = true) { return addr == 0x27 ? 0 : 2; }
  uint8_t requestFrom(uint8_t a, uint8_t k) { return a == 0x27 ? k : 0; }
  int read() { if (reg == 0x12) return (uint8_t)~g_fake_btns; return 0xFF; }
};
extern FakeWire Wire;
