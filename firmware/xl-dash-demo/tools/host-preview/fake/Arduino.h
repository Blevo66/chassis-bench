// Host-side stand-in for the Arduino core, only for compile-checking and preview renders.
#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <algorithm>
using std::min; using std::max;
extern uint64_t g_us;
inline uint32_t millis() { return g_us / 1000; }
inline uint32_t micros() { return (uint32_t)g_us; }
inline void delay(uint32_t ms) { g_us += ms * 1000ull; }
inline void yield() {}
#define PI 3.14159265358979f
#define DEG_TO_RAD 0.017453292519943295f
#define RAD_TO_DEG 57.29577951308232f
#define OUTPUT 1
#define HIGH 1
#define SERIAL_8N1 0
template <class T, class L, class H> T constrain(T v, L lo, H hi) { return v < lo ? lo : (v > hi ? hi : v); }
inline void pinMode(int, int) {}
inline void digitalWrite(int, int) {}
struct FakeSerial {
  void begin(int, int = 0, int = 0, int = 0) {}
  int available() { return 0; } int read() { return -1; }
  void println(const char *s) { fprintf(stderr, "%s\n", s); }
  template <class... A> void printf(const char *f, A... a) { fprintf(stderr, f, a...); }
};
extern FakeSerial Serial, Serial1;
// Names the real ESP32-S3 core defines in pins_arduino.h (so clashes show up here too)
static const uint8_t TX = 43, RX = 44, SDA = 8, SCL = 9, SS = 10, MOSI = 11, MISO = 13, SCK = 12;
static const uint8_t A0 = 1, A1 = 2, A2 = 3, A3 = 4, A4 = 5, A5 = 6, A6 = 7, A7 = 8, A8 = 9, A9 = 10, A10 = 11,
  A11 = 12, A12 = 13, A13 = 14, A14 = 15, A15 = 16, A16 = 17, A17 = 18, A18 = 19, A19 = 20;
static const uint8_t T1 = 1, T2 = 2, T3 = 3, T4 = 4, T5 = 5, T6 = 6, T7 = 7, T8 = 8, T9 = 9, T10 = 10, T11 = 11, T12 = 12, T13 = 13, T14 = 14;
