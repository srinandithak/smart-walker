#include <Wire.h>
#include <vl53l4cd_class.h>

// ── DRIVE MOTORS ──────────────────────────────────────────────
const int ENA = 5;   // left motor speed (PWM)
const int IN1 = 7;
const int IN2 = 8;

const int ENB = 6;   // right motor speed (PWM)
const int IN3 = 10;
const int IN4 = 11;

// ── VIBRATION MOTORS ──────────────────────────────────────────
const int VIB_L_EN  = 3;
const int VIB_L_IN1 = 4;
const int VIB_L_IN2 = 2;

const int VIB_R_EN  = 9;
const int VIB_R_IN1 = 12;
const int VIB_R_IN2 = 13;

// ── FORCE SENSORS ─────────────────────────────────────────────
const int LEFT_FSR  = A0;
const int RIGHT_FSR = A1;

float smoothLeft  = 0;
float smoothRight = 0;
const float ALPHA = 0.2;

// ── DISTANCE SENSOR (VL53L4CD, I2C) ──────────────────────────
VL53L4CD distSensor(&Wire, -1);

// ── TIMING ────────────────────────────────────────────────────
unsigned long lastFsrSend = 0;
const unsigned long FSR_INTERVAL_MS = 50;  // 20 Hz

// ─────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Drive motors
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  // Set default forward direction
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);

  // Vibration motors
  pinMode(VIB_L_EN, OUTPUT); pinMode(VIB_L_IN1, OUTPUT); pinMode(VIB_L_IN2, OUTPUT);
  pinMode(VIB_R_EN, OUTPUT); pinMode(VIB_R_IN1, OUTPUT); pinMode(VIB_R_IN2, OUTPUT);

  // Set vibration motor direction
  digitalWrite(VIB_L_IN1, HIGH); digitalWrite(VIB_L_IN2, LOW);
  digitalWrite(VIB_R_IN1, HIGH); digitalWrite(VIB_R_IN2, LOW);

  // Distance sensor
  Wire.begin();
  distSensor.begin();
  distSensor.VL53L4CD_Off();
  distSensor.InitSensor();
  distSensor.VL53L4CD_SetRangeTiming(50, 0);
  distSensor.VL53L4CD_StartRanging();

  Serial.println("READY");
}

// ─────────────────────────────────────────────────────────────
// Motor helpers
// ─────────────────────────────────────────────────────────────
void stopDrive() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void stopVibration() {
  analogWrite(VIB_L_EN, 0);
  analogWrite(VIB_R_EN, 0);
}

void stopAll() {
  stopDrive();
  stopVibration();
}

void moveLeft() {
  analogWrite(ENA, 180);
  analogWrite(ENB, 80);   // slow right wheel → turns left
}

void moveRight() {
  analogWrite(ENA, 80);   // slow left wheel → turns right
  analogWrite(ENB, 180);
}

void vibLeft(int speed)  { analogWrite(VIB_L_EN, speed); }
void vibRight(int speed) { analogWrite(VIB_R_EN, speed); }

// ─────────────────────────────────────────────────────────────
// Force sensor helpers
// ─────────────────────────────────────────────────────────────
int smoothValue(float &smooth, int raw) {
  smooth = ALPHA * raw + (1.0 - ALPHA) * smooth;
  return (int)smooth;
}

// ─────────────────────────────────────────────────────────────
void loop() {

  // ── 1. Handle commands from Jetson ──────────────────────────
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    stopAll();

    if (cmd.indexOf('L') >= 0) {
      moveLeft();
    } else if (cmd.indexOf('R') >= 0) {
      moveRight();
    }
    // 'S' or empty → already stopped above

    if (cmd.indexOf('V') >= 0) {
      vibLeft(255);
      vibRight(255);
    }
  }

  // ── 2. Send force sensor readings to Jetson (20 Hz) ─────────
  unsigned long now = millis();
  if (now - lastFsrSend >= FSR_INTERVAL_MS) {
    lastFsrSend = now;
    int rawLeft  = analogRead(LEFT_FSR);
    int rawRight = analogRead(RIGHT_FSR);
    int left  = smoothValue(smoothLeft,  rawLeft);
    int right = smoothValue(smoothRight, rawRight);
    // Format: "left,right\n"  — matches read_forces.py parser
    Serial.print(left);
    Serial.print(",");
    Serial.println(right);
  }

  // ── 3. Poll distance sensor and send reading ─────────────────
  uint8_t newDataReady = 0;
  distSensor.VL53L4CD_CheckForDataReady(&newDataReady);
  if (newDataReady) {
    VL53L4CD_Result_t result;
    distSensor.VL53L4CD_GetResult(&result);
    distSensor.VL53L4CD_ClearInterrupt();
    // Format: "D:<mm>\n"
    Serial.print("D:");
    Serial.println(result.distance_mm);
  }
}
