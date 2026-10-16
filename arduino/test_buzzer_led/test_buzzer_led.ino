// Test 3: Buzzer + LED. Yarim saniye arayla birlikte yanip otmeli.
const int BUZZER_PIN = 8;
const int LED_PIN = 7;

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(BUZZER_PIN, HIGH);
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
