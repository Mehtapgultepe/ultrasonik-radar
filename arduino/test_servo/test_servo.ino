// Test 2: Sadece SG90 servo. 0-180 arasi gidip donmeli.
#include <Servo.h>
const int SERVO_PIN = 12;
Servo servo;

void setup() {
  servo.attach(SERVO_PIN);
}

void loop() {
  for (int aci = 0; aci <= 180; aci++) { servo.write(aci); delay(15); }
  delay(500);
  for (int aci = 180; aci >= 0; aci--) { servo.write(aci); delay(15); }
  delay(500);
}
