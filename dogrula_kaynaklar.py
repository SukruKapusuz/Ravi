#!/usr/bin/env python3
"""RÂVÎ - kaynaklar.py'deki tüm RSS linklerini test eder.

Uygulamayı etkilemez; isteğe bağlı bir araçtır. Çalıştırmak için:

    pip install feedparser
    python dogrula_kaynaklar.py

Her kaynağa tek tek bakar, sonucu ekrana yazar ve bozuk olanları
bozuk_kaynaklar.txt dosyasına kaydeder (kaynaklar.py'den o satırları
silmeniz ya da düzeltmeniz için).
"""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser

from kaynaklar import HABER_ISTASYONU

socket.setdefaulttimeout(10)


def test_et(kaynak_adi, kategori_adi, url):
    try:
        besleme = feedparser.parse(url)
    except Exception as hata:
        return "HATA", str(hata)
    if besleme.bozo and not besleme.entries:
        return "BOZUK", str(besleme.get("bozo_exception", "ayrıştırılamadı"))
    if not besleme.entries:
        return "BOŞ", "haber bulunamadı"
    return "TAMAM", f"{len(besleme.entries)} haber"


def main():
    isler = [(kaynak_adi, kategori_adi, url)
             for kaynak_adi, kategoriler in HABER_ISTASYONU.items()
             for kategori_adi, url in kategoriler.items()]
    print(f"{len(isler)} kaynak test ediliyor (bu birkaç dakika sürebilir)...\n")

    sonuclar, bozuklar = [], []
    with ThreadPoolExecutor(max_workers=12) as havuz:
        gelecekler = {havuz.submit(test_et, *i): i for i in isler}
        for gelecek in as_completed(gelecekler):
            kaynak_adi, kategori_adi, url = gelecekler[gelecek]
            durum, detay = gelecek.result()
            sonuclar.append((kaynak_adi, kategori_adi, url, durum, detay))
            if durum != "TAMAM":
                bozuklar.append((kaynak_adi, kategori_adi, url, durum, detay))

    sonuclar.sort(key=lambda s: (s[3] != "TAMAM", s[0], s[1]))
    for kaynak_adi, kategori_adi, url, durum, detay in sonuclar:
        isaret = "✅" if durum == "TAMAM" else "❌"
        print(f"{isaret} [{durum:5}] {kaynak_adi} | {kategori_adi} — {detay}")

    print(f"\n{len(isler) - len(bozuklar)}/{len(isler)} kaynak çalışıyor.")
    if bozuklar:
        with open("bozuk_kaynaklar.txt", "w", encoding="utf-8") as f:
            for kaynak_adi, kategori_adi, url, durum, detay in bozuklar:
                f.write(f"{kaynak_adi} | {kategori_adi} | {url} | {durum}: {detay}\n")
        print(f"{len(bozuklar)} bozuk kaynak 'bozuk_kaynaklar.txt' dosyasına yazıldı.")


if __name__ == "__main__":
    main()
