#pragma once
#include <Arduino.h>
struct TCA9554 { TCA9554(uint8_t) {} bool begin(uint8_t = 0, uint8_t = 0) { return true; }
  bool pinMode1(uint8_t, uint8_t) { return true; } bool write1(uint8_t, uint8_t) { return true; } };
