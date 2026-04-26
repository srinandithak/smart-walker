#include <Wire.h>
#include <vl53l4cd_class.h>

// Create sensor object (-1 means no shutdown pin)
VL53L4CD sensor(&Wire, -1);

// Motor pins (update these to match YOUR wiring)
const int ENA = 5;   // left motor speed (PWM)
const int ENB = 6;   // right motor speed (PWM)
const int IN1 = 7;   // left motor direction
const int IN2 = 8;
const int IN3 = 9;   // right motor direction
const int IN4 = 10;
const int VIB = 3;   // vibration motor

void setup() {
    Serial.begin(115200);
    
    // Motor pins
    pinMode(ENA, OUTPUT);
    pinMode(ENB, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    pinMode(VIB, OUTPUT);
    
    // Motors forward by default
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    
    // Initialize I2C
    Wire.begin();
    
    // Initialize sensor
    sensor.begin();
    sensor.VL53L4CD_Off();
    sensor.InitSensor();
    sensor.VL53L4CD_SetRangeTiming(50, 0);  // 50ms budget, continuous
    sensor.VL53L4CD_StartRanging();
    
    Serial.println("READY");
}

void loop() {
    // --- READ DISTANCE SENSOR ---
    uint8_t NewDataReady = 0;
    VL53L4CD_Result_t results;
    
    sensor.VL53L4CD_CheckForDataReady(&NewDataReady);
    
    if (NewDataReady) {
        sensor.VL53L4CD_GetResult(&results);
        sensor.VL53L4CD_ClearInterrupt();
        
        // Send distance to Jetson
        Serial.print("D:");
        Serial.println(results.distance_mm);
    }
    
    // --- HANDLE COMMANDS FROM JETSON ---
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        
        if (cmd.indexOf('L') >= 0) {
            analogWrite(ENA, 80);
            analogWrite(ENB, 180);
        } 
        else if (cmd.indexOf('R') >= 0) {
            analogWrite(ENA, 180);
            analogWrite(ENB, 80);
        } 
        else if (cmd.indexOf('S') >= 0) {
            analogWrite(ENA, 0);
            analogWrite(ENB, 0);
        }
        
        if (cmd.indexOf('V') >= 0) {
            analogWrite(VIB, 200);
        } else {
            analogWrite(VIB, 0);
        }
    }
    
    delay(10);
}
