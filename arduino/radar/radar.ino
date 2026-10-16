// =============================================================
//  Ultrasonik Sensorlu Radar - Ana Arduino Kodu
//  Servo 0-180 derece tarar, her acida mesafe olcer,
//  "aci,mesafe\n" formatinda seri porta gonderir.
//  mesafe = 0  ->  o acida gecerli nesne yok
// =============================================================
#include <Servo.h>

// ---- Pin plani (ekipce sabit) ----
const int TRIG_PIN   = 10;
const int ECHO_PIN   = 11;
const int SERVO_PIN  = 12;
const int BUZZER_PIN = 8;
const int LED_PIN    = 7;

// ---- Tarama ayarlari ----
const int MIN_ACI = 0;
const int MAX_ACI = 180;
const int ADIM    = 2;                 // derece
const unsigned long SERVO_BEKLEME_MS = 30;   // servonun yerine oturmasi icin

// ---- Olcum ayarlari ----
const int OLCUM_SAYISI = 3;            // her acida alinan olcum (medyan alinir)
const int MIN_MESAFE   = 2;            // cm
const int MAX_MESAFE   = 200;          // cm (guvenilir aralik)
const unsigned long ECHO_TIMEOUT = 12000UL;  // us, ~200 cm'ye karsilik gelir

// ---- Uyari ayarlari ----
const int UYARI_ESIGI = 20;            // cm, bunun altinda uyari
const unsigned long EN_HIZLI_BIP = 60;   // ms, nesne cok yakinken
const unsigned long EN_YAVAS_BIP = 400;  // ms, nesne esige yakinken

Servo servo;
int uyariMesafe = 0;                   // uyari sisteminin baktigi son mesafe
bool bipAcik = false;
unsigned long sonBipZamani = 0;

// -------------------------------------------------------------
// Tek olcum: cm cinsinden mesafe, gecersizse -1
// -------------------------------------------------------------
int olcMesafe() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long sure = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT);
  if (sure == 0) return -1;            // yankı gelmedi

  int mesafe = (int)(sure * 0.0343 / 2.0 + 0.5);
  if (mesafe < MIN_MESAFE || mesafe > MAX_MESAFE) return -1;
  return mesafe;
}

// -------------------------------------------------------------
// Birkac olcumun medyani: tek bir hatali olcumu eler
// -------------------------------------------------------------
int olcFiltreli() {
  int degerler[OLCUM_SAYISI];
  int n = 0;

  for (int i = 0; i < OLCUM_SAYISI; i++) {
    int m = olcMesafe();
    if (m > 0) degerler[n++] = m;
    bekle(10);                         // onceki yankinin sonmesi icin
  }
  if (n == 0) return -1;

  // kucukten buyuge siralama (insertion sort)
  for (int i = 1; i < n; i++) {
    int anahtar = degerler[i];
    int j = i - 1;
    while (j >= 0 && degerler[j] > anahtar) {
      degerler[j + 1] = degerler[j];
      j--;
    }
    degerler[j + 1] = anahtar;
  }
  return degerler[n / 2];
}

// -------------------------------------------------------------
// Uyari sistemi
// uyariKontrol(): yeni mesafeyi bildirir
// uyariGuncelle(): buzzer/LED'i millis() ile surer (kodu durdurmaz)
// -------------------------------------------------------------
void uyariGuncelle() {
  if (uyariMesafe <= 0 || uyariMesafe >= UYARI_ESIGI) {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    bipAcik = false;
    return;
  }

  digitalWrite(LED_PIN, HIGH);

  // nesne yaklastikca bip araligi kisalir
  unsigned long aralik = map(uyariMesafe, MIN_MESAFE, UYARI_ESIGI,
                             EN_HIZLI_BIP, EN_YAVAS_BIP);
  unsigned long simdi = millis();
  if (simdi - sonBipZamani >= aralik) {
    bipAcik = !bipAcik;
    digitalWrite(BUZZER_PIN, bipAcik ? HIGH : LOW);
    sonBipZamani = simdi;
  }
}

void uyariKontrol(int mesafe) {
  uyariMesafe = mesafe;
  uyariGuncelle();
}

// delay() yerine: beklerken uyari sistemi calismaya devam eder
void bekle(unsigned long ms) {
  unsigned long baslangic = millis();
  while (millis() - baslangic < ms) {
    uyariGuncelle();
  }
}

// -------------------------------------------------------------
// Bir aciyi tara: servoyu dondur, olc, gonder, uyar
// -------------------------------------------------------------
void tara(int aci) {
  servo.write(aci);
  bekle(SERVO_BEKLEME_MS);

  int mesafe = olcFiltreli();
  if (mesafe < 0) mesafe = 0;          // 0 = nesne yok

  Serial.print(aci);
  Serial.print(',');
  Serial.println(mesafe);              // satir sonu: \n

  uyariKontrol(mesafe);
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  servo.attach(SERVO_PIN);
  servo.write(MIN_ACI);
  Serial.begin(9600);
  delay(500);
}

void loop() {
  for (int aci = MIN_ACI; aci <= MAX_ACI; aci += ADIM) tara(aci);
  for (int aci = MAX_ACI; aci >= MIN_ACI; aci -= ADIM) tara(aci);
}
