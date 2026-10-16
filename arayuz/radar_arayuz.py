"""
Ultrasonik Radar - Arayuz (Python + Pygame)

Kullanim:
  python radar_arayuz.py --port COM3              # gercek Arduino
  python radar_arayuz.py --sahte                  # Arduino olmadan sahte veriyle
  python radar_arayuz.py --port COM3 --csv        # ayrica olcumler.csv'ye kaydet
  python radar_arayuz.py --port COM3 --menzil 100 # ekranda gosterilen en buyuk mesafe (cm)

Veri formati: her satir "aci,mesafe" (ornek: 45,30). mesafe=0 -> nesne yok.
"""
import argparse
import csv
import datetime
import math
import random
import sys
import time

import pygame

BAUD = 9600
GENISLIK, YUKSEKLIK = 1000, 620
MERKEZ = (GENISLIK // 2, YUKSEKLIK - 90)
YARICAP = 440
UYARI_ESIGI = 20          # cm, Arduino'daki ile ayni olmali
SOLMA_SURESI = 3.0        # sn, eski noktalar bu surede kaybolur

SIYAH = (0, 0, 0)
YESIL = (40, 255, 90)
KOYU_YESIL = (20, 110, 40)
KIRMIZI = (255, 50, 50)
BEYAZ = (230, 230, 230)


# ---------------------------------------------------------------
# Veri kaynaklari
# ---------------------------------------------------------------
def satir_ayristir(satir):
    """'45,30' -> (45, 30). Bozuk satirda None doner."""
    try:
        aci_str, mesafe_str = satir.strip().split(",")
        aci, mesafe = int(aci_str), int(float(mesafe_str))
    except ValueError:
        return None
    if not (0 <= aci <= 180) or mesafe < 0:
        return None
    return aci, mesafe


class SeriKaynak:
    def __init__(self, port):
        import serial  # pip install pyserial
        self.ser = serial.Serial(port, BAUD, timeout=0)
        self.tampon = ""

    def oku(self):
        """Gelen tum tam satirlari (aci, mesafe) listesi olarak dondurur."""
        veri = self.ser.read(self.ser.in_waiting or 1).decode(errors="ignore")
        self.tampon += veri
        olcumler = []
        while "\n" in self.tampon:
            satir, self.tampon = self.tampon.split("\n", 1)
            sonuc = satir_ayristir(satir)
            if sonuc:
                olcumler.append(sonuc)
        return olcumler

    def kapat(self):
        self.ser.close()


class SahteKaynak:
    """Arduino yokken arayuzu gelistirmek icin: iki sabit nesne + gurultu."""
    def __init__(self):
        self.aci, self.yon = 0, 2
        self.son = time.time()
        self.nesneler = [(40, 55, 25), (110, 130, 15)]  # (aci_bas, aci_son, cm)

    def oku(self):
        if time.time() - self.son < 0.03:
            return []
        self.son = time.time()
        mesafe = 0
        for bas, son, cm in self.nesneler:
            if bas <= self.aci <= son:
                mesafe = cm + random.randint(-1, 1)
        olcum = (self.aci, mesafe)
        self.aci += self.yon
        if self.aci >= 180 or self.aci <= 0:
            self.yon = -self.yon
            self.aci = max(0, min(180, self.aci))
        return [olcum]

    def kapat(self):
        pass


# ---------------------------------------------------------------
# Cizim
# ---------------------------------------------------------------
def kutupsal(aci, uzaklik_px):
    rad = math.radians(aci)
    return (MERKEZ[0] + uzaklik_px * math.cos(rad),
            MERKEZ[1] - uzaklik_px * math.sin(rad))


def zemin_ciz(ekran, font, menzil):
    # mesafe halkalari
    halka_adim = max(10, menzil // 4)
    for cm in range(halka_adim, menzil + 1, halka_adim):
        r = int(cm / menzil * YARICAP)
        kutu = pygame.Rect(MERKEZ[0] - r, MERKEZ[1] - r, 2 * r, 2 * r)
        pygame.draw.arc(ekran, KOYU_YESIL, kutu, 0, math.pi, 2)
        ekran.blit(font.render(f"{cm} cm", True, KOYU_YESIL),
                   (MERKEZ[0] + r + 4, MERKEZ[1] + 4))
    # aci cizgileri
    for aci in range(0, 181, 30):
        pygame.draw.line(ekran, KOYU_YESIL, MERKEZ, kutupsal(aci, YARICAP), 1)
        x, y = kutupsal(aci, YARICAP + 22)
        yazi = font.render(f"{aci}°", True, KOYU_YESIL)
        ekran.blit(yazi, yazi.get_rect(center=(x, y)))
    pygame.draw.line(ekran, KOYU_YESIL,
                     (MERKEZ[0] - YARICAP, MERKEZ[1]),
                     (MERKEZ[0] + YARICAP, MERKEZ[1]), 2)


def nesneleri_ciz(ekran, noktalar, menzil):
    simdi = time.time()
    for aci, (mesafe, zaman) in noktalar.items():
        yas = simdi - zaman
        if mesafe <= 0 or mesafe > menzil or yas > SOLMA_SURESI:
            continue
        parlaklik = 1 - yas / SOLMA_SURESI
        renk = (int(255 * parlaklik), int(50 * parlaklik), int(50 * parlaklik))
        bas = kutupsal(aci, mesafe / menzil * YARICAP)
        son = kutupsal(aci, YARICAP)
        pygame.draw.line(ekran, renk, bas, son, 3)   # nesnenin arkasi "golge"
        pygame.draw.circle(ekran, renk, (int(bas[0]), int(bas[1])), 5)


def tarama_ciz(ekran, aci):
    # iz efekti: son birkac derece soluk
    for i in range(12):
        a = aci - i if aci - i >= 0 else 0
        renk = (0, max(40, 255 - i * 18), 0)
        pygame.draw.line(ekran, renk, MERKEZ, kutupsal(a, YARICAP), 2)


def panel_ciz(ekran, font, aci, mesafe, menzil, kayit_var):
    if mesafe <= 0:
        durum, renk = "Nesne yok", YESIL
    elif mesafe < UYARI_ESIGI:
        durum, renk = "UYARI: Nesne cok yakin!", KIRMIZI
    elif mesafe <= menzil:
        durum, renk = "Nesne algilandi", KIRMIZI
    else:
        durum, renk = "Menzil disi", YESIL

    mesafe_yazi = f"{mesafe} cm" if mesafe > 0 else "-"
    y = YUKSEKLIK - 50
    ekran.blit(font.render(f"Aci: {aci}°", True, BEYAZ), (30, y))
    ekran.blit(font.render(f"Mesafe: {mesafe_yazi}", True, BEYAZ), (200, y))
    ekran.blit(font.render(durum, True, renk), (420, y))
    if kayit_var:
        ekran.blit(font.render("● CSV kaydi", True, KIRMIZI), (GENISLIK - 160, y))


# ---------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", help="Seri port, orn. COM3 veya /dev/ttyUSB0")
    ap.add_argument("--sahte", action="store_true", help="Arduino olmadan sahte veri")
    ap.add_argument("--csv", nargs="?", const="olcumler.csv",
                    help="Olcumleri CSV'ye kaydet (varsayilan: olcumler.csv)")
    ap.add_argument("--menzil", type=int, default=50, help="Ekran menzili (cm)")
    args = ap.parse_args()

    if args.sahte:
        kaynak = SahteKaynak()
    elif args.port:
        kaynak = SeriKaynak(args.port)
    else:
        sys.exit("--port COMx veya --sahte vermelisiniz.")

    csv_dosya = csv_yazici = None
    if args.csv:
        csv_dosya = open(args.csv, "w", newline="", encoding="utf-8")
        csv_yazici = csv.writer(csv_dosya)
        csv_yazici.writerow(["zaman", "aci", "mesafe_cm"])

    pygame.init()
    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("Ultrasonik Radar")
    font = pygame.font.SysFont("consolas", 18)
    saat = pygame.time.Clock()

    noktalar = {}            # aci -> (mesafe, zaman)
    son_aci, son_mesafe = 0, 0

    try:
        calisiyor = True
        while calisiyor:
            for olay in pygame.event.get():
                if olay.type == pygame.QUIT or (
                        olay.type == pygame.KEYDOWN and olay.key == pygame.K_ESCAPE):
                    calisiyor = False

            for aci, mesafe in kaynak.oku():
                noktalar[aci] = (mesafe, time.time())
                son_aci, son_mesafe = aci, mesafe
                if csv_yazici:
                    zaman = datetime.datetime.now().isoformat(timespec="milliseconds")
                    csv_yazici.writerow([zaman, aci, mesafe])

            ekran.fill(SIYAH)
            zemin_ciz(ekran, font, args.menzil)
            nesneleri_ciz(ekran, noktalar, args.menzil)
            tarama_ciz(ekran, son_aci)
            panel_ciz(ekran, font, son_aci, son_mesafe, args.menzil, csv_yazici is not None)
            pygame.display.flip()
            saat.tick(60)
    finally:
        kaynak.kapat()
        if csv_dosya:
            csv_dosya.close()
        pygame.quit()


if __name__ == "__main__":
    main()
