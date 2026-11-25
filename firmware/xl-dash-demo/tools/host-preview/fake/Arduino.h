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
