"""RÂVÎ - Güncelleme kontrolü.

İnternette ayrı bir sunucumuz olmadığı için GitHub'ın herkese açık Releases
API'sini kullanırız: kimlik/şifre gerekmez, yalnızca okunur. Hiçbir dosya
indirilmez ya da üzerine yazılmaz; yalnızca "daha yeni bir sürüm var mı"
sorusuna cevap bulunur. Evetse, indirme sayfası tarayıcıda açılır ve kurulumu
kullanıcı kendisi yapar (bkz. ravi.py).
"""
import json
import re
import urllib.error
import urllib.request

GITHUB_REPO = "SukruKapusuz/Ravi"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
ZAMAN_ASIMI = 6  # saniye


def surumu_ayikla(metin):
    """'v1.2.0', '1.2.0-beta', 'Sürüm 1.2' gibi metinlerden (major, minor, patch) çıkarır."""
    if not metin:
        return None
    eslesme = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", str(metin))
    if not eslesme:
        return None
    buyuk, kucuk, yama = eslesme.groups()
    return (int(buyuk), int(kucuk), int(yama or 0))


def surum_karsilastir(a, b):
    """a > b ise pozitif, a < b ise negatif, eşitse 0 döner. Ayrıştırılamayan sürüm en küçük sayılır."""
    ta, tb = surumu_ayikla(a) or (-1, -1, -1), surumu_ayikla(b) or (-1, -1, -1)
    return (ta > tb) - (ta < tb)


def en_son_surumu_al():
    """GitHub'daki en son "release"i döner: {"surum", "baslik", "url"} ya da ağ/veri
    hatasında None. Hiçbir istisna dışarı sızmaz; çağıran yalnızca None kontrolü yapar."""
    istek = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "RAVI-Haber-Merkezi"},
    )
    try:
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
            veri = json.loads(yanit.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    if not isinstance(veri, dict):
        return None
    etiket, url = veri.get("tag_name"), veri.get("html_url")
    if not etiket or not url or not surumu_ayikla(etiket):
        return None
    return {"surum": etiket, "baslik": veri.get("name") or etiket, "url": url}


def guncelleme_var_mi(mevcut_surum):
    """(bool, bilgi|None) döner. bilgi, en_son_surumu_al'ın döndürdüğü sözlüktür."""
    bilgi = en_son_surumu_al()
    if bilgi is None:
        return False, None
    return surum_karsilastir(bilgi["surum"], mevcut_surum) > 0, bilgi
