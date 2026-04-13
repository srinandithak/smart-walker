const int leftFSR = A0;
const int rightFSR = A1;

float smoothLeft = 0;
float smoothRight = 0;

float alpha = 0.2;

void setup() {
  Serial.begin(115200);
}

int smoothValue(float &smooth, int raw) {
  smooth = alpha * raw + (1 - alpha) * smooth;
  return (int)smooth;
}

void loop() {
  int leftRaw = analogRead(leftFSR);
  int rightRaw = analogRead(rightFSR);

  int leftValue = smoothValue(smoothLeft, leftRaw);
  int rightValue = smoothValue(smoothRight, rightRaw);

  Serial.print(leftValue);
  Serial.print(",");
  Serial.println(rightValue);

  delay(50);
}