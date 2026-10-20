"""RÂVÎ - Mizan: haberleri kullanıcının ilgisine göre sıralayan motor.

Bu dosya sadece hesap yapar: arayüze ve diske dokunmaz, yalnızca Python'un
standart kütüphanelerini kullanır. Profil sıradan bir sözlüktür (bkz. bos_profil);
okuma/yazma işini depo.py yapar.

Puan formülü:
    haber puanı = kaynak puanı * 1.5 + kelime puanları (üst/alt sınırlı)
                  + güncellik bonusu - (okunmuşsa 50)
"""
import calendar
import re
import time

# ----------------------------------------------------------------- ayarlar
# "Seçilen Haberler" ve "Keşfet" artık ayrı sekmeler olduğundan iki ayrı havuz
# hesaplanır. Havuzlar SAYFA_BOYUTU'ndan büyük tutulur; "Daha Fazla Göster"
# yeni bir ağ isteği yapmadan bu havuzun bir sonraki dilimini açar.
HAVUZ_SECILEN = 150         # Seçilen Haberler'de biriktirilen aday sayısı
HAVUZ_KESIF = 60            # Keşfet'te biriktirilen aday sayısı
KESIF_KAYNAK_BASINA = 4     # Keşfet'te bir kaynaktan en fazla kaç haber
SAYFA_BOYUTU_SECILEN = 20   # her "Daha Fazla Göster" tıklamasında açılan haber sayısı
SAYFA_BOYUTU_KESIF = 10

KAYNAK_CARPANI = 1.5
OKUNMUS_CEZASI = 50.0
GUNCELLIK_AZAMI = 10.0      # yeni çıkmış haberin bonusu
GUNCELLIK_YARI_OMUR = 12.0  # saat: bonus her 12 saatte yarıya iner
GUNCELLIK_NOTR = 3.0        # yayın zamanı okunamayan haberlere verilen bonus

PUAN_UST, PUAN_ALT = 30.0, -20.0     # tek bir kaynağın / kelimenin puan sınırı
KELIME_TOPLAM_SINIR = 40.0           # bir başlıktaki kelimelerden gelen toplam (±)
KOK_UZUNLUK = 5
KELIME_AZAMI = 300          # profilde tutulan kelime sayısı
LISTE_AZAMI = 200           # okunan / gizlenen bağlantı sayısı
SOGUMA_GUNLUK = 0.95        # puanlar her gün %5 erir
SOGUMA_ALT_SINIR = 0.1      # bundan küçük puanlar silinir

DURAK = frozenset("""
ve ile için bir bu şu da de ki mi mı mu mü gibi ama fakat ancak çok daha en kadar
sonra önce her hem veya ise olarak olan oldu olur var yok ne nasıl neden ilk
son dakika flaş video foto galeri haber haberi haberler
""".split())

_HARFLER = re.compile(r"[a-zçğıöşüâîû]+")


# ------------------------------------------------------------- yardımcılar
def bos_profil():
    """Profilin şeması. depo.py da aynı şemayı kullanır."""
    return {
        "ogrenme": True,    # kapalıysa ne kaydedilir ne de sıralamada kullanılır
        "kaynak": {},       # {"NTV | Ekonomi": 6.0}
        "kelime": {},       # {"ekono": 3.0}
        "okunan": [],       # tıklanan son haber bağlantıları
        "gizli": [],        # "Gizle" ile kaldırılan son haber bağlantıları
        "son_islem": 0.0,   # soğuma hesabı için zaman damgası
    }


def tr_kucuk(metin):
    """Türkçe'ye uygun küçük harf: İ -> i, I -> ı (str.lower() bunları bozar)."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def kokler(baslik):
    """Başlıktan kelime köklerini çıkarır: gereksiz kelimeler atılır, ilk 5 harf alınır."""
    sonuc = []
    for kelime in _HARFLER.findall(tr_kucuk(baslik or "")):
        if len(kelime) < 3 or kelime in DURAK:
            continue
        kok = kelime[:KOK_UZUNLUK]
        if kok not in sonuc:
            sonuc.append(kok)
    return sonuc


def tarih_zamani(ayrisik_tarih):
    """feedparser'ın (UTC) tarih bilgisini saniyeye çevirir; okunamazsa None."""
    try:
        return float(calendar.timegm(ayrisik_tarih)) if ayrisik_tarih else None
    except (TypeError, ValueError, OverflowError):
        return None


def _sinirla(deger):
    return min(PUAN_UST, max(PUAN_ALT, deger))


def _guncellik(tarih, simdi):
    if tarih is None:
        return GUNCELLIK_NOTR
    yas_saat = max(0.0, (simdi - tarih) / 3600.0)
    return GUNCELLIK_AZAMI * 0.5 ** (yas_saat / GUNCELLIK_YARI_OMUR)


# ----------------------------------------------------------------- puanlama
def puan_hesapla(haber, profil, simdi, okundu=False):
    kaynak = profil["kaynak"].get(haber["kaynak"], 0.0)
    kelime = sum(profil["kelime"].get(k, 0.0) for k in kokler(haber["baslik"]))
    kelime = max(-KELIME_TOPLAM_SINIR, min(KELIME_TOPLAM_SINIR, kelime))
    puan = kaynak * KAYNAK_CARPANI + kelime + _guncellik(haber.get("tarih"), simdi)
    return puan - (OKUNMUS_CEZASI if okundu else 0.0)


def _puanla_ve_tekille(haberler, profil, simdi):
    """Ortak ilk adım: puanla, gizlenenleri at, yinelenen linki tekille, puana göre sırala."""
    gizli, okunan = set(profil["gizli"]), set(profil["okunan"])
    en_iyi, adaylar = {}, []
    for sira, h in enumerate(haberler):
        link = h.get("link") or ""
        if link and link in gizli:
            continue
        okundu = bool(link) and link in okunan
        aday = dict(h, puan=puan_hesapla(h, profil, simdi, okundu), okundu=okundu, _sira=sira)
        if link and link in en_iyi and en_iyi[link]["puan"] >= aday["puan"]:
            continue
        en_iyi[link] = aday
        adaylar.append(aday)
    adaylar = [a for a in adaylar if not a["link"] or en_iyi[a["link"]] is a]
    adaylar.sort(key=lambda a: (-a["puan"], -(a["tarih"] or 0.0), a["_sira"]))
    return adaylar


def sec_ve_kesfet(haberler, profil, simdi=None):
    """Haberleri iki ayrı sekmeye böler ve her ikisi için de sıralı bir HAVUZ döner.

    Dönen sözlük: {"secilen": [...], "kesif": [...]}. Her liste, ekranda bir
    sekmede gösterilebilecek olandan daha büyük tutulur (bkz. HAVUZ_SECILEN /
    HAVUZ_KESIF); ekran bunun bir SAYFA_BOYUTU kadarını gösterir, "Daha Fazla
    Göster" bir sonraki dilimi açar. Ağa yeniden gidilmez.

    - secilen: tüm adaylar, yalnızca puana göre sıralı (kullanıcı kaynakları
      zaten kendi seçtiği için kaynak kotası uygulanmaz).
    - kesif: "secilen" havuzunda az yer bulan/ilgisi düşük kaynaklardan,
      kaynak başına sınırlı, en güncel haberler (çeşitlilik için).
    """
    simdi = simdi or time.time()
    adaylar = _puanla_ve_tekille(haberler, profil, simdi)
    secilen = adaylar[:HAVUZ_SECILEN]

    # Keşfet: "Seçilen"in tersine, kaynak kotasıyla sınırlı değil kaynak
    # ÇEŞİTLİLİĞİ içindir. İlgisi nötr/düşük kaynaklardan (puanı <= 0, yani
    # henüz sevilmemiş ya da hiç denenmemiş), kaynak başına en fazla
    # KESIF_KAYNAK_BASINA kadar, en güncel ve okunmamış haber döner.
    # Tek kaynak seçiliyse keşfedilecek bir şey yoktur (zaten hepsi Seçilen'de).
    kesif = []
    tum_kaynaklar = {a["kaynak"] for a in adaylar}
    if len(tum_kaynaklar) >= 2:
        kaynak_puan = {a["kaynak"]: profil["kaynak"].get(a["kaynak"], 0.0) for a in adaylar}
        adaylar_kaynak = [k for k, p in kaynak_puan.items() if p <= 0.0] or list(kaynak_puan)
        kaynak_sirasi = sorted(adaylar_kaynak, key=lambda k: (kaynak_puan[k], k))

        by_kaynak = {}
        for a in adaylar:
            if not a["okundu"]:
                by_kaynak.setdefault(a["kaynak"], []).append(a)
        for liste in by_kaynak.values():
            liste.sort(key=lambda a: (-(a["tarih"] or 0.0), a["_sira"]))

        kaynak_adet = {k: 0 for k in kaynak_sirasi}
        indeks = {k: 0 for k in kaynak_sirasi}
        degisti = True
        while len(kesif) < HAVUZ_KESIF and degisti:
            degisti = False
            for k in kaynak_sirasi:
                if len(kesif) >= HAVUZ_KESIF:
                    break
                if kaynak_adet[k] >= KESIF_KAYNAK_BASINA:
                    continue
                liste = by_kaynak.get(k, [])
                i = indeks[k]
                if i < len(liste):
                    kesif.append(liste[i])
                    indeks[k] = i + 1
                    kaynak_adet[k] += 1
                    degisti = True

    return {"secilen": secilen, "kesif": kesif}


# ---------------------------------------------------------------- öğrenme
def _kirp(profil):
    if len(profil["kelime"]) > KELIME_AZAMI:
        en_guclu = sorted(profil["kelime"].items(), key=lambda kv: abs(kv[1]), reverse=True)
        profil["kelime"] = dict(en_guclu[:KELIME_AZAMI])


def ogren(profil, haber, olay):
    """'ac' (habere tıklandı) ya da 'gizle' olayını profile işler. Öğrenme kapalıysa hiçbir şey yapmaz."""
    if not profil.get("ogrenme", True):
        return
    if olay == "ac":
        kaynak_fark, kelime_fark, liste = 2.0, 1.0, profil["okunan"]
    elif olay == "gizle":
        kaynak_fark, kelime_fark, liste = -1.0, -2.0, profil["gizli"]
    else:
        return

    ad = haber["kaynak"]
    profil["kaynak"][ad] = _sinirla(profil["kaynak"].get(ad, 0.0) + kaynak_fark)
    for kok in kokler(haber["baslik"]):
        profil["kelime"][kok] = _sinirla(profil["kelime"].get(kok, 0.0) + kelime_fark)

    link = haber.get("link")
    if link:
        if link in liste:
            liste.remove(link)
        liste.append(link)
        del liste[:-LISTE_AZAMI]
    _kirp(profil)


def sogut(profil, simdi=None):
    """Geçen güne göre puanları eritir. Profil değiştiyse True döner (diske yazılmalı)."""
    simdi = simdi or time.time()
    onceki = profil.get("son_islem") or 0.0
    if not onceki:
        profil["son_islem"] = simdi
        return True
    gun = (simdi - onceki) / 86400.0
    if gun < 1.0:
        return False
    faktor = SOGUMA_GUNLUK ** gun
    for ad in ("kaynak", "kelime"):
        eriyen = {k: v * faktor for k, v in profil[ad].items()}
        profil[ad] = {k: v for k, v in eriyen.items() if abs(v) >= SOGUMA_ALT_SINIR}
    profil["son_islem"] = simdi
    return True
