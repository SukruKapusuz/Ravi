"""RÂVÎ - Yerel veri deposu.

Kullanıcılar, kalıcı oturum ve ayarlar, programın çalıştığı klasöre değil
işletim sisteminin kullanıcı veri klasörüne yazılır. Böylece program tek
dosyaya (exe) paketlendiğinde de veriler kaybolmaz:

    Windows : %APPDATA%\\RAVI
    Linux   : ~/.config/ravi   (XDG_CONFIG_HOME varsa orası)
    macOS   : ~/Library/Application Support/RAVI
"""
import hashlib
import hmac
import json
import os
import secrets
import shutil
import sys

_SIFRE_ON_EK = "pbkdf2$"
_TUR = 200_000


def veri_klasoru():
    if sys.platform.startswith("win"):
        taban = os.environ.get("APPDATA") or os.path.expanduser("~")
        yol = os.path.join(taban, "RAVI")
    elif sys.platform == "darwin":
        yol = os.path.expanduser("~/Library/Application Support/RAVI")
    else:
        taban = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        yol = os.path.join(taban, "ravi")
    os.makedirs(yol, exist_ok=True)
    return yol


VERI_KLASORU = veri_klasoru()
KULLANICILAR = os.path.join(VERI_KLASORU, "kullanicilar.json")
OTURUM = os.path.join(VERI_KLASORU, "oturum.json")
AYARLAR = os.path.join(VERI_KLASORU, "ayarlar.json")


# ------------------------------------------------------------- dosya işleri
def _json_oku(yol, varsayilan):
    try:
        with open(yol, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return varsayilan


def _json_yaz(yol, veri):
    """Önce geçici dosyaya yazar, sonra yerine koyar (yarım yazılmış dosya kalmaz)."""
    gecici = yol + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)
    try:
        os.chmod(gecici, 0o600)  # Linux/macOS: sadece sahibi okuyabilsin
    except OSError:
        pass
    os.replace(gecici, yol)


def _eski_veriyi_tasi():
    """Eski sürümde çalışma klasöründe duran kullanicilar.json varsa bir kez kopyalar."""
    if os.path.exists(KULLANICILAR):
        return
    adaylar = (
        os.path.join(os.getcwd(), "kullanicilar.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "kullanicilar.json"),
    )
    for aday in adaylar:
        if os.path.exists(aday):
            try:
                shutil.copy(aday, KULLANICILAR)
            except OSError:
                pass
            return


_eski_veriyi_tasi()


# ------------------------------------------------------------------ şifreler
def _hashle(sifre, tuz=None):
    tuz = tuz or secrets.token_hex(16)
    ozet = hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), bytes.fromhex(tuz), _TUR).hex()
    return f"{_SIFRE_ON_EK}{tuz}${ozet}"


def _dogrula(sifre, saklanan):
    try:
        _, tuz, ozet = saklanan.split("$")
    except ValueError:
        return False
    yeni = _hashle(sifre, tuz).split("$")[2]
    return hmac.compare_digest(yeni.encode(), ozet.encode())


# ---------------------------------------------------------------- kullanıcılar
def verileri_oku():
    veri = _json_oku(KULLANICILAR, {})
    return veri if isinstance(veri, dict) else {}


def verileri_yaz(veriler):
    _json_yaz(KULLANICILAR, veriler)


def kullanici_ekle(isim, sifre):
    """Yeni kullanıcı oluşturur. Aynı isim varsa dokunmaz ve False döner."""
    sifre = sifre.strip()
    veriler = verileri_oku()
    if isim in veriler:
        return False
    veriler[isim] = {"sifre": _hashle(sifre), "tercihler": []}
    verileri_yaz(veriler)
    return True


def giris_kontrol(isim, sifre):
    """(durum, tercihler) döner. Eski düz metin şifreler ilk girişte otomatik hashlenir."""
    sifre = sifre.strip()
    veriler = verileri_oku()
    kayit = veriler.get(isim)
    if not isinstance(kayit, dict):
        return False, None

    saklanan = str(kayit.get("sifre", ""))
    if saklanan.startswith(_SIFRE_ON_EK):
        dogru = _dogrula(sifre, saklanan)
    else:
        dogru = hmac.compare_digest(saklanan.strip().encode("utf-8"), sifre.encode("utf-8"))
        if dogru:
            kayit["sifre"] = _hashle(sifre)
            verileri_yaz(veriler)

    if dogru:
        return True, kayit.get("tercihler", [])
    return False, None


def tercihleri_oku(isim):
    kayit = verileri_oku().get(isim)
    if isinstance(kayit, dict):
        return kayit.get("tercihler", []) or []
    return []


def tercihleri_kaydet(isim, tercihler):
    veriler = verileri_oku()
    if isim in veriler:
        veriler[isim]["tercihler"] = tercihler
        verileri_yaz(veriler)


# ------------------------------------------------------------ kalıcı oturum
def _jeton_ozeti(jeton):
    return hashlib.sha256(jeton.encode("utf-8")).hexdigest()


def oturum_kaydet(isim):
    """Rastgele bir jeton üretir: jetonun kendisi oturum.json'da, özeti kullanıcı kaydında durur.
    Şifre hiçbir yerde düz metin olarak saklanmaz."""
    veriler = verileri_oku()
    if isim not in veriler:
        return
    jeton = secrets.token_hex(32)
    veriler[isim]["jeton"] = _jeton_ozeti(jeton)
    verileri_yaz(veriler)
    _json_yaz(OTURUM, {"kullanici": isim, "jeton": jeton})


def oturum_oku():
    """Geçerli bir hatırlanmış oturum varsa kullanıcı adını, yoksa None döner."""
    d = _json_oku(OTURUM, {})
    isim, jeton = d.get("kullanici"), d.get("jeton")
    if not isim or not jeton:
        return None
    kayit = verileri_oku().get(isim)
    if not isinstance(kayit, dict) or "jeton" not in kayit:
        return None
    if hmac.compare_digest(_jeton_ozeti(jeton).encode(), str(kayit["jeton"]).encode()):
        return isim
    return None


def oturum_sil(isim=None):
    try:
        os.remove(OTURUM)
    except OSError:
        pass
    if isim:
        veriler = verileri_oku()
        if isim in veriler and "jeton" in veriler[isim]:
            veriler[isim].pop("jeton")
            verileri_yaz(veriler)


# ------------------------------------------------------------------- ayarlar
def ayar_oku(anahtar, varsayilan=None):
    return _json_oku(AYARLAR, {}).get(anahtar, varsayilan)


def ayar_yaz(anahtar, deger):
    ayarlar = _json_oku(AYARLAR, {})
    ayarlar[anahtar] = deger
    _json_yaz(AYARLAR, ayarlar)
