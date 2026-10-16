"""
Ultrasonik Radar - CSV Kayit Scripti (arayuz olmadan, test icin)

Kullanim:
  python veri_kayit.py --port COM3
  python veri_kayit.py --port COM3 --dosya test1_10cm.csv --sure 60
  python veri_kayit.py --port COM3 --aci 90      # sadece 90 derecedeki olcumler

Not: Ayni anda arayuz de porta bagliysa bu script portu acamaz.
Arayuzle birlikte kayit istiyorsaniz: radar_arayuz.py --csv
Ctrl+C ile durdurulur.
"""
import argparse
import csv
import datetime
import time

import serial  # pip install pyserial

BAUD = 9600


def satir_ayristir(satir):
    try:
        aci_str, mesafe_str = satir.strip().split(",")
        aci, mesafe = int(aci_str), int(float(mesafe_str))
    except ValueError:
        return None
    if not (0 <= aci <= 180) or mesafe < 0:
        return None
    return aci, mesafe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="Seri port, orn. COM3")
    ap.add_argument("--dosya", default="olcumler.csv", help="Cikti CSV dosyasi")
    ap.add_argument("--sure", type=float, help="Kayit suresi (sn), verilmezse Ctrl+C'ye kadar")
    ap.add_argument("--aci", type=int, help="Sadece bu acidaki olcumleri kaydet")
    args = ap.parse_args()

    ser = serial.Serial(args.port, BAUD, timeout=1)
    time.sleep(2)                 # Arduino port acilinca resetlenir, bekle
    ser.reset_input_buffer()

    sayac, baslangic = 0, time.time()
    with open(args.dosya, "w", newline="", encoding="utf-8") as f:
        yazici = csv.writer(f)
        yazici.writerow(["zaman", "aci", "mesafe_cm"])
        print(f"Kayit basladi -> {args.dosya}  (durdurmak icin Ctrl+C)")
        try:
            while args.sure is None or time.time() - baslangic < args.sure:
                satir = ser.readline().decode(errors="ignore")
                sonuc = satir_ayristir(satir)
                if not sonuc:
                    continue
                aci, mesafe = sonuc
                if args.aci is not None and aci != args.aci:
                    continue
                zaman = datetime.datetime.now().isoformat(timespec="milliseconds")
                yazici.writerow([zaman, aci, mesafe])
                sayac += 1
                print(f"{zaman}  aci={aci:3d}  mesafe={mesafe:3d} cm")
        except KeyboardInterrupt:
            pass
    ser.close()
    print(f"\nBitti. {sayac} olcum kaydedildi.")


if __name__ == "__main__":
    main()
