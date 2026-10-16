"""
Test 1 analizi: CSV'deki olcumlerin ortalama, sapma ve yuzde hatasini hesaplar.

Kullanim:
  python analiz.py test1_10cm.csv --gercek 10
"""
import argparse
import csv
import statistics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dosya")
    ap.add_argument("--gercek", type=float, required=True, help="Gercek mesafe (cm)")
    args = ap.parse_args()

    with open(args.dosya, encoding="utf-8") as f:
        olcumler = [int(r["mesafe_cm"]) for r in csv.DictReader(f) if int(r["mesafe_cm"]) > 0]

    if not olcumler:
        print("Gecerli olcum yok.")
        return

    ort = statistics.mean(olcumler)
    sapma = statistics.stdev(olcumler) if len(olcumler) > 1 else 0.0
    mutlak = abs(ort - args.gercek)
    yuzde = mutlak / args.gercek * 100

    print(f"Olcum sayisi     : {len(olcumler)}")
    print(f"Gercek mesafe    : {args.gercek:.1f} cm")
    print(f"Ortalama olcum   : {ort:.2f} cm")
    print(f"Standart sapma   : {sapma:.2f} cm")
    print(f"Mutlak hata      : {mutlak:.2f} cm")
    print(f"Yuzde hata       : {yuzde:.2f} %")


if __name__ == "__main__":
    main()
