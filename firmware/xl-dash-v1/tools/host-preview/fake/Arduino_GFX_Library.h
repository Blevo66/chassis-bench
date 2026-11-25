// Stand-ins with the same constructor signatures as GFX Library for Arduino 1.5.5.
#pragma once
#include <Arduino.h>
#define GFX_NOT_DEFINED -1
#define FSPI 0
extern double g_spi_hz;
extern uint16_t g_screen[480 * 320];
struct Arduino_DataBus { virtual ~Arduino_DataBus() {} };
struct Arduino_ESP32SPI : Arduino_DataBus {
  Arduino_ESP32SPI(int8_t dc = -1, int8_t cs = -1, int8_t sck = -1, int8_t mosi = -1, int8_t miso = -1, uint8_t spi_num = FSPI, bool shared = true) {}
};
struct Arduino_GFX {
  virtual ~Arduino_GFX() {}
  virtual bool begin(int32_t speed = GFX_NOT_DEFINED) { g_spi_hz = speed > 0 ? speed : 40e6; return true; }
  void fillScreen(uint16_t c) { for (auto &p : g_screen) p = c; }
  virtual void draw16bitRGBBitmap(int16_t x, int16_t y, uint16_t *bmp, int16_t w, int16_t h) {
    for (int j = 0; j < h; j++) for (int i = 0; i < w; i++) g_screen[(y + j) * 480 + x + i] = bmp[j * w + i];
    g_us += (uint64_t)((w * h * 16.0 + 64) / g_spi_hz * 1e6 * 1.4);   // SPI time estimate (+40% overhead, a guess)
  }
  void setTextColor(uint16_t) {} void setTextSize(uint8_t) {} void setCursor(int16_t, int16_t) {}
  void println(const char *s) { fprintf(stderr, "LCD: %s\n", s); }
};
struct Arduino_ST7796 : Arduino_GFX {
  Arduino_ST7796(Arduino_DataBus *bus, int8_t rst = -1, uint8_t r = 0, bool ips = false, int16_t w = 320, int16_t h = 480,
                 uint8_t c1 = 0, uint8_t r1 = 0, uint8_t c2 = 0, uint8_t r2 = 0) {}
};
