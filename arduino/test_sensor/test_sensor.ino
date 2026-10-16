// Test 1: Sadece HC-SR04. Serial Monitor (9600) acip mesafeyi izleyin.
const int TRIG_PIN = 10;
const int ECHO_PIN = 11;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long sure = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (sure == 0) {
    Serial.println("Yanki yok");
  } else {
    float mesafe = sure * 0.0343 / 2.0;
    Serial.print("Mesafe: ");
    Serial.print(mesafe);
    Serial.println(" cm");
  }
  delay(200);
}
