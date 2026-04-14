// Left drive motor
const int ENA = 5;
const int IN1 = 7;
const int IN2 = 8;

// Right drive motor
const int ENB = 6;
const int IN3 = 10;
const int IN4 = 11;

// Left vibration motor
const int VIB_L_EN = 3;
const int VIB_L_IN1 = 4;
const int VIB_L_IN2 = 2;

// Right vibration motor
const int VIB_R_EN = 9;
const int VIB_R_IN1 = 12;
const int VIB_R_IN2 = 13;



void setup() {
  Serial.begin(115200);

  // Movement motors
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Vibration motors
  pinMode(VIB_L_EN, OUTPUT);
  pinMode(VIB_L_IN1, OUTPUT);
  pinMode(VIB_L_IN2, OUTPUT);

  pinMode(VIB_R_EN, OUTPUT);
  pinMode(VIB_R_IN1, OUTPUT);
  pinMode(VIB_R_IN2, OUTPUT);
}



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
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, 180);
  analogWrite(ENB, 80); // slow right wheel → turn left
}

void moveRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, 80);
  analogWrite(ENB, 180); // slow left wheel → turn right
}


void vibLeft(int speed) {
  digitalWrite(VIB_L_IN1, HIGH);
  digitalWrite(VIB_L_IN2, LOW);
  analogWrite(VIB_L_EN, speed);
}

void vibRight(int speed) {
  digitalWrite(VIB_R_IN1, HIGH);
  digitalWrite(VIB_R_IN2, LOW);
  analogWrite(VIB_R_EN, speed);
}


void loop() {

  if (Serial.available()) {

    char cmd = Serial.read();

    stopAll(); // reset every cycle

    if (cmd == 'L') {
      moveLeft();
      vibRight(255);
    }

    else if (cmd == 'R') {
      moveRight();
      vibLeft(255);
    }

    else if (cmd == 'S') {
      stopAll();
    }
  }
}