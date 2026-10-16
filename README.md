# Ultrasonik Radar Projesi

HC-SR04 + SG90 ile 0–180° tarama yapan radar. Arduino veriyi seri porta gönderir, Python arayüzü çizer.

## Ortak kurallar
- **Pinler:** Trig D10, Echo D11, Servo D12, Buzzer D8, LED D7
- **Format:** `aci,mesafe\n` (ör. `45,30`), mesafe tam sayı cm, `0` = nesne yok
- **Baud:** 9600 · **Uyarı eşiği:** 20 cm

## Klasörler
| Klasör | İçerik |
|---|---|
| `arduino/radar` | Ana Arduino kodu |
| `arduino/test_*` | Sensör, servo, buzzer/LED test kodları |
| `arayuz` | Radar ekranı (Pygame) |
| `veri_kayit` | CSV kayıt ve analiz scriptleri |

## Çalıştırma
```bash
pip install -r requirements.txt
python arayuz/radar_arayuz.py --sahte             # Arduino olmadan
python arayuz/radar_arayuz.py --port COM3 --csv   # gerçek veri + kayıt
python veri_kayit/veri_kayit.py --port COM3 --aci 90 --sure 30
python veri_kayit/analiz.py olcumler.csv --gercek 10
```
Arayüzü çalıştırmadan önce Arduino IDE'deki Serial Monitor'ü kapatın; port aynı anda tek programa açılır.
