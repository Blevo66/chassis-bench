// =====================================================================
//  XL125R ignition-battery sender  (ESP32-C3 SuperMini)
//  v0.1, untested on hardware.
//
//  Wakes every SLEEP_S seconds, reads the ignition pack voltage (and current,
//  if the optional INA226 is fitted), broadcasts it in a Bluetooth LE advert
//  for ~150 ms, then deep-sleeps. The dash listens for the advert (passive scan), so the
//  two looms share no wires at all.
//
//  Wire it AFTER the ignition key / kill switch so it draws nothing when the
//  bike is off. Advert payload (manufacturer data, 9 bytes):
//    FF FF 'X' 'L' mV_lo mV_hi mA_lo mA_hi seq     (mA = 0xFFFF: no current sensor)
//  0xFFFF is the "no company" test ID; fine for a private bike gadget.
// =====================================================================
#include <Arduino.h>
#include <NimBLEDevice.h>
#include <Wire.h>

static const int      PIN_VBAT   = 0;                          // GPIO0 = ADC1_CH0
static const float    DIVIDER    = (1000.0f + 100.0f) / 100.0f; // 1M top, 100k bottom
static const float    CAL        = 1.000f;                     // trim against a meter
static const uint32_t SLEEP_S    = 5;                          // update period
static const uint32_t ADVERT_MS  = 150;                        // radio on-time per wake

// Optional INA226 current sensor (I2C). Swap the module's 0.1 R shunt for 0.01 R
// so it reads up to ~8 A. If it isn't found, voltage comes from the divider.
static const int      PIN_SDA    = 8, PIN_SCL = 9;              // SuperMini I2C
static const uint8_t  INA_ADDR   = 0x40;
static const float    SHUNT_OHM  = 0.010f;

RTC_DATA_ATTR uint8_t seq = 0;

bool inaWrite(uint8_t reg, uint16_t v) {
  Wire.beginTransmission(INA_ADDR); Wire.write(reg); Wire.write(v >> 8); Wire.write(v & 0xFF);
  return Wire.endTransmission() == 0;
}
bool inaRead(uint8_t reg, int16_t& out) {
  Wire.beginTransmission(INA_ADDR); Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)INA_ADDR, 2) != 2) return false;
  out = (int16_t)((Wire.read() << 8) | Wire.read());
  return true;
}

void setup() {
  uint32_t packMv = 0, packMa = 0xFFFF;
  Wire.begin(PIN_SDA, PIN_SCL);
  // 16-sample average, 1.1 ms conversions, continuous shunt + bus (0x4527)
  if (inaWrite(0x00, 0x4527)) {
    delay(40);
    int16_t sh, bus;
    if (inaRead(0x01, sh) && inaRead(0x02, bus)) {
      float amps = sh * 2.5e-6f / SHUNT_OHM;                   // shunt LSB 2.5 uV
      packMv = (uint32_t)(bus * 1.25f * CAL);                  // bus LSB 1.25 mV
      packMa = amps < 0 ? 0 : (uint32_t)(amps * 1000.0f);
      if (packMa > 65534) packMa = 65534;
    }
  }
  if (packMv == 0) {                                           // no INA226: use the divider
    analogSetPinAttenuation(PIN_VBAT, ADC_11db);
    uint32_t mv = 0;
    for (int i = 0; i < 16; i++) mv += analogReadMilliVolts(PIN_VBAT);
    mv /= 16;
    packMv = (uint32_t)(mv * DIVIDER * CAL);
  }
  if (packMv > 65535) packMv = 65535;

  NimBLEDevice::init("");
  NimBLEDevice::setPower(ESP_PWR_LVL_P9);                       // short range is fine, but be heard over the engine
  NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
  NimBLEAdvertisementData d;
  std::string m;
  m += (char)0xFF; m += (char)0xFF; m += 'X'; m += 'L';
  m += (char)(packMv & 0xFF); m += (char)(packMv >> 8);
  m += (char)(packMa & 0xFF); m += (char)(packMa >> 8); m += (char)seq++;
  d.setFlags(0x06);
  d.setManufacturerData(m);
  adv->setAdvertisementData(d);
  adv->setMinInterval(32);                                     // 20 ms (units of 0.625 ms)
  adv->setMaxInterval(40);                                     // 25 ms
  adv->start();
  delay(ADVERT_MS);
  adv->stop();
  NimBLEDevice::deinit(true);

  esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_S * 1000000ULL);
  esp_deep_sleep_start();
}

void loop() {}
