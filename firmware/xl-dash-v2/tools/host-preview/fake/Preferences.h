#pragma once
struct Preferences { bool begin(const char *, bool) { return true; } double getDouble(const char *, double d) { return d + 4817.3; } size_t putDouble(const char *, double) { return 8; } };
