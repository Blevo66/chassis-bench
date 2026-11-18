# Ignition-battery sender (v0.1)

A thumbnail-sized ESP32-C3 that sits on the ignition Li-ion pack and tells the dash its voltage over Bluetooth. **There is no wire between the engine loom and the body loom.** If this board dies, the engine doesn't care; the dash just shows `IGN --`.

**Status: NOT compiled or tested.** Written blind in the cloud (build tools blocked). Expect small fixes on first build.

## Parts (prices are rough guesses)

| Part | Notes |
|---|---|
| ESP32-C3 SuperMini | ~£3. Remove or cut its power LED to save current. |
| 3.3 V buck regulator, 20 V+ input, low no-load current | e.g. Pololu D36V6F3. Feeds the C3's 3V3 pin. |
| 1 MΩ + 100 kΩ resistors, 100 nF capacitor | Voltage divider into GPIO0. Cap across the 100k. Reads up to ~34 V. |
| INA226 current-sensor module (optional, ~£3) | For live current and an accurate time-left. **Swap its 0.1 Ω shunt for 0.01 Ω** (R010, 2512 size) so it reads up to ~8 A. I2C: SDA→GPIO8, SCL→GPIO9, VCC→3V3. Put its IN+/IN− in the pack + feed. If fitted, it also measures the voltage, so the divider is optional. |
| 2 A inline fuse | At the battery end of the feed. |
| Heatshrink or a little printed capsule | Mount it near the battery, foam-backed. |

## Wiring

```
Ignition pack + ── fuse ── key / kill switch ── [INA226 IN+ → IN−] ──┬── CDI
                                                                   ├── buck IN+ ── buck 3V3 ── C3 3V3
                                                                   └── 1M ──┬── GPIO0
                                                                            ├── 100k ── GND
                                                                            └── 100nF ── GND
Ignition pack − ───────────────────────────────── buck GND ── C3 GND
```

Taking the feed **after** the key / kill switch means it draws nothing when the bike is parked.

## Numbers (estimates, measure on the bench)

- Awake ~150 ms every 5 s. Average current maybe ~0.5–1 mA including the regulator. Next to a CDI drawing roughly 0.5–1 A that's about 0.1%.
- Bluetooth range easily covers tank-to-tower. Carbon blocks radio, so keep the board outside any carbon cover or give it a plastic window.

## Time left

The dash works out roughly how long the ignition will keep running:

- **Charge left** from the pack voltage using a typical Li-ion curve and your pack capacity (`IGN_CAPACITY_MAH`). Rough: maybe ±10–15%, because voltage sags under load.
- **Draw** from the INA226 (averaged over a few minutes), or the fixed `IGN_ASSUMED_MA` if no sensor is fitted. Measure that once with a meter at a fast idle.

The CDI's current comes in pulses with each spark, so single readings jump about. The dash smooths them.

## Calibrate

Measure the pack with a meter, compare with what the dash shows, set `CAL` in `src/main.cpp` (e.g. meter 14.62, dash 14.48 → `CAL = 1.0097`), reflash.

## Dash side

`firmware/xl-dash` listens for the advert (NimBLE passive scan). Pack size and warning levels are in `xl-dash/src/config.h`: `IGN_CELLS`, `IGN_WARN_PER_CELL`, `IGN_LOW_PER_CELL`.
