// XL brain box: reads the left controller, RPM and brake, drives the 8 MOSFET outputs,
// and tells the screen what it's doing over a serial link. Works with NO screen attached:
// lights, indicators and horn don't depend on it.
#pragma once

// ------------------------------------------------------------------ state
struct Brain {
  uint8_t btn = 0;            // bit n = MCP pin n pressed
  int mcpAddr = -1;           // -1 = button chip not found
  bool indL = false, indR = false, hazard = false;
  bool lightsOn = false, high = false, flash = false, horn = false, drl = true;
  bool brake = false, beam = false;
  bool out[8] = {};
  float rpm = 0;
  int screenPage = -1;        // page the screen says it's showing (-1 = no screen)
  uint32_t screenSeenMs = 0;
} B;

static char lastEvent[48] = "press a button";
static uint32_t eventCount = 0;

// ------------------------------------------------------------------ link to the screen
// Lines of text, NMEA style:  $<body>*<2 hex XOR of body>\n
//   box -> screen  $S,rpm,flags,btn,outs,mcp,eventCount,held0..held4,lastEvent   (20 times a second)
//                  $E,PAGE        next page           $E,TRIP   reset trip A
//   screen -> box  $P,page                                                         (5 times a second)
// flags bits: 0 indL 1 indR 2 hazard 3 high 4 flash 5 horn 6 lightsOn 7 drl 8 brake 9 beam
static void linkSend(const char *body) {
  uint8_t cs = 0;
  for (const char *p = body; *p; p++) cs ^= (uint8_t)*p;
  LINK_SERIAL.printf("$%s*%02X\n", body, cs);
}
static void logEvent(const char *s) {
  snprintf(lastEvent, sizeof lastEvent, "%s", s); eventCount++;
  Serial.printf("[button] %s\n", s);
}

static char rxLine[64]; static int rxLen = 0;
static void linkLine(char *s) {
  char *star = strrchr(s, '*');
  if (s[0] != '$' || !star) return;
  *star = 0;
  uint8_t cs = 0;
  for (char *p = s + 1; *p; p++) cs ^= (uint8_t)*p;
  if (cs != (uint8_t)strtol(star + 1, nullptr, 16)) return;   // garbled: ignore
  if (s[1] == 'P' && s[2] == ',') { B.screenPage = atoi(s + 3); B.screenSeenMs = millis(); }
}
static void linkPoll() {
  while (LINK_SERIAL.available()) {
    char c = LINK_SERIAL.read();
    if (c == '\n' || c == '\r') { if (rxLen) { rxLine[rxLen] = 0; linkLine(rxLine); rxLen = 0; } }
    else if (rxLen < (int)sizeof(rxLine) - 1) rxLine[rxLen++] = c;
    else rxLen = 0;
  }
  if (millis() - B.screenSeenMs > 1000) B.screenPage = -1;    // screen gone: box carries on alone
}

// ------------------------------------------------------------------ left controller
static bool i2cWrite(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission() == 0;
}
static int i2cRead(uint8_t addr, uint8_t reg) {
  Wire.beginTransmission(addr); Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(addr, (uint8_t)1) != 1) return -1;
  return Wire.read();
}
static void mcpFind() {
  B.mcpAddr = -1;
  for (int a = 0x20; a <= 0x27; a++) {
    if (i2cWrite(a, 0x00, 0xFF) && i2cWrite(a, 0x0C, 0xFF)) {   // IODIRA inputs, GPPUA pull-ups
      if (i2cRead(a, 0x00) == 0xFF) { B.mcpAddr = a; break; }
    }
  }
  if (B.mcpAddr < 0) Serial.println("Button chip (MCP23017) not found at 0x20-0x27");
  else Serial.printf("Button chip (MCP23017) found at 0x%02X\n", B.mcpAddr);
}
static void mcpRead() {
  static uint32_t lastTry = 0, lastRead = 0;
  if (B.mcpAddr < 0) {
    B.btn = 0;
    if (millis() - lastTry > 2000) { lastTry = millis(); mcpFind(); }
    return;
  }
  if (millis() - lastRead < 5) return;
  lastRead = millis();
  int v = i2cRead(B.mcpAddr, 0x12);
  if (v < 0) { B.mcpAddr = -1; B.btn = 0; lastTry = millis(); return; }
  B.btn = (uint8_t)~v;
}

struct Button { int pin; bool down = false, held = false, lastRaw = false; uint32_t changedMs = 0, downMs = 0; };
static Button bL{BTN_IND_L}, bR{BTN_IND_R}, bHorn{BTN_HORN}, bLights{BTN_LIGHTS}, bMode{BTN_MODE};
static Button *const BUTTONS[5] = {&bL, &bR, &bHorn, &bLights, &bMode};
// 0 nothing, 1 tap (on release), 2 hold reached
static int pollButton(Button &b) {
  bool raw = B.btn & (1 << b.pin);
  uint32_t now = millis();
  if (raw != b.lastRaw) { b.lastRaw = raw; b.changedMs = now; }
  if (now - b.changedMs < DEBOUNCE_MS) return 0;
  if (raw && !b.down) { b.down = true; b.held = false; b.downMs = now; }
  if (raw && b.down && !b.held && now - b.downMs >= HOLD_MS) { b.held = true; return 2; }
  if (!raw && b.down) { b.down = false; if (!b.held) return 1; }
  return 0;
}

static void handleButtons() {
  mcpRead();
  uint32_t now = millis();
  int e;
  if ((e = pollButton(bL))) {
    if (e == 1) { B.hazard = false; B.indR = false; B.indL = !B.indL; logEvent(B.indL ? "IND L tap = left ON" : "IND L tap = left off"); }
    else        { B.hazard = !B.hazard; B.indL = B.indR = false; logEvent(B.hazard ? "IND L hold = hazards ON" : "IND L hold = hazards off"); }
  }
  if ((e = pollButton(bR))) {
    if (e == 1) { B.hazard = false; B.indL = false; B.indR = !B.indR; logEvent(B.indR ? "IND R tap = right ON" : "IND R tap = right off"); }
    else        { B.hazard = !B.hazard; B.indL = B.indR = false; logEvent(B.hazard ? "IND R hold = hazards ON" : "IND R hold = hazards off"); }
  }
  if (pollButton(bHorn) == 1) logEvent("HORN pressed");
  B.horn = B.btn & (1 << BTN_HORN);                        // straight from the switch, no delay

  // LIGHTS: hold = headlight on (low) / off, tap = high / low while it's on. DRL always on.
  static bool lightsDone = false;
  if (pollButton(bLights) == 1) {
    if (!B.lightsOn) logEvent("LIGHTS tap: headlight off, hold 3 s");
    else { B.high = !B.high; logEvent(B.high ? "LIGHTS tap = HIGH beam" : "LIGHTS tap = low beam"); }
  }
  if (!bLights.down) lightsDone = false;
  else if (!lightsDone && now - bLights.downMs >= LIGHTS_OFF_MS) {
    B.lightsOn = !B.lightsOn; B.high = false; lightsDone = true;
    logEvent(B.lightsOn ? "LIGHTS hold 3 s = headlight ON (low)" : "LIGHTS hold 3 s = headlight OFF");
  }

  // MODE: tap = flash high beam, hold = next page. On the TRIP page (1): let go = next page,
  // keep holding = reset trip A. Pages and trips live in the screen, so those are messages.
  static uint32_t passUntil = 0;
  static bool modeWaiting = false;
  if ((e = pollButton(bMode))) {
    if (e == 1) { passUntil = now + PASS_FLASH_MS; logEvent("MODE tap = flash high beam"); }
    else if (B.screenPage == 1) modeWaiting = true;
    else { linkSend("E,PAGE"); logEvent("MODE hold = next page"); }
  }
  if (modeWaiting) {
    if (!bMode.down) { modeWaiting = false; linkSend("E,PAGE"); logEvent("MODE hold = next page"); }
    else if (now - bMode.downMs >= TRIP_RESET_MS) { modeWaiting = false; linkSend("E,TRIP"); logEvent("MODE hold 3 s = trip A RESET"); }
  }
  B.flash = (int32_t)(passUntil - now) > 0;
}

// ------------------------------------------------------------------ outputs
static bool flashPhase() { return (millis() % FLASH_PERIOD_MS) < FLASH_PERIOD_MS / 2; }
static void writeOutputs() {
  bool f = flashPhase(), w[8];
  w[O_IND_L] = (B.indL || B.hazard) && f;
  w[O_IND_R] = (B.indR || B.hazard) && f;
  bool highOn = (B.lightsOn && B.high) || B.flash;     // flash works even with the headlight off
  w[O_HIGH] = highOn;
  w[O_LOW]  = B.lightsOn && (!highOn || LOW_WITH_HIGH);
  w[O_HORN] = B.horn;
  w[O_USB]  = true;
  w[O_DRL]  = B.drl;
  w[O_TAIL] = true;
  for (int i = 0; i < 8; i++) {
    B.out[i] = w[i];
    if (PIN_OUT[i] < 0) continue;
    if (i == O_TAIL || i == O_DRL) {
      float d = !w[i] ? 0.0f : (i == O_TAIL) ? TAIL_DUTY : (B.lightsOn ? DRL_DIM_DUTY : 1.0f);
      if (!OUT_ACTIVE_HIGH) d = 1.0f - d;
      ledcWrite(PIN_OUT[i], (uint32_t)(d * 255.0f + 0.5f));
    } else digitalWrite(PIN_OUT[i], w[i] == OUT_ACTIVE_HIGH ? HIGH : LOW);
  }
  B.beam = highOn;
}

// ------------------------------------------------------------------ inputs
// Brake: tail PWM pulls the opto low only TAIL_DUTY of the time; the brake switch holds it low.
static void readBrake() {
  static uint32_t last = 0;
  if (millis() - last < 20) return;
  last = millis();
  const uint32_t stepUs = (1300000UL / PWM_HZ) / 16;
  for (int i = 0; i < 16; i++) {
    if (digitalRead(PIN_BRAKE) != LOW) { B.brake = false; return; }
    delayMicroseconds(stepUs);
  }
  B.brake = true;
}
static volatile uint32_t rpmLastUs = 0, rpmPeriodUs = 0;
static void IRAM_ATTR rpmISR() {
  uint32_t now = micros(), dt = now - rpmLastUs;
  if (dt < RPM_LOCKOUT_US) return;
  rpmPeriodUs = dt; rpmLastUs = now;
}
static void updateRpm() {
  noInterrupts(); uint32_t period = rpmPeriodUs, last = rpmLastUs; interrupts();
  B.rpm = (period > 0 && (micros() - last) < RPM_TIMEOUT_MS * 1000UL) ? 60.0e6f / (period * SPARKS_PER_REV) : 0;
}

// ------------------------------------------------------------------ setup and loop
void brainSetup() {
  // outputs first, all off
  for (int i = 0; i < 8; i++) if (PIN_OUT[i] >= 0) { pinMode(PIN_OUT[i], OUTPUT); digitalWrite(PIN_OUT[i], OUT_ACTIVE_HIGH ? LOW : HIGH); }
  ledcAttach(PIN_OUT[O_TAIL], PWM_HZ, 8);       // esp32 core 3.x API
  ledcAttach(PIN_OUT[O_DRL], PWM_HZ, 8);
  Serial.begin(115200);
  pinMode(PIN_BRAKE, INPUT_PULLUP);
  pinMode(PIN_RPM, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), rpmISR, RISING);
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(I2C_HZ);
  mcpFind();
  LINK_SERIAL.begin(LINK_BAUD, SERIAL_8N1, LINK_RX_PIN, LINK_TX_PIN);
  writeOutputs();                                // DRL + tail on straight away
  Serial.println("XL brain box running");
}

void brainLoop() {
  linkPoll();
  handleButtons();
  readBrake();
  updateRpm();
  writeOutputs();

  static uint32_t lastSend = 0;
  if (millis() - lastSend >= 50) {               // 20 times a second
    lastSend = millis();
    uint32_t flags = B.indL | B.indR << 1 | B.hazard << 2 | B.high << 3 | B.flash << 4 | B.horn << 5 |
                     B.lightsOn << 6 | B.drl << 7 | B.brake << 8 | B.beam << 9;
    uint32_t outs = 0;
    for (int i = 0; i < 8; i++) outs |= (uint32_t)B.out[i] << i;
    int held[5];
    for (int i = 0; i < 5; i++) held[i] = BUTTONS[i]->down ? (int)((millis() - BUTTONS[i]->downMs) / 100) : 0;
    char body[120];
    snprintf(body, sizeof body, "S,%d,%u,%u,%u,%d,%u,%d,%d,%d,%d,%d,%s", (int)B.rpm, (unsigned)flags, B.btn,
             (unsigned)outs, B.mcpAddr, (unsigned)(eventCount & 0xFFFF), held[0], held[1], held[2], held[3], held[4], lastEvent);
    linkSend(body);
  }
}
