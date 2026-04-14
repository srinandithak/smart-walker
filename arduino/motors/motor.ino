// LEFT motor
const int ENA = 5;
const int IN1 = 7;
const int IN2 = 8;

// RIGHT motor
const int ENB = 6;
const int IN3 = 10;
const int IN4 = 11;

// Vibration motor
const int VIB = 9;

void setup() {
  Serial.begin(115200);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(VIB, OUTPUT);
}

void stopAll() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  analogWrite(VIB, 0);
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    stopAll();

    for (int i = 0; i < line.length(); i++) {
      char c = line[i];

      if (c == 'L') {
        // LEFT motor forward
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 200);
      }
      else if (c == 'R') {
        // RIGHT motor forward
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 200);
      }
      else if (c == 'V') {
        analogWrite(VIB, 255);
      }
    }
  }
}