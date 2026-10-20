#!/usr/bin/env python3
"""RÂVÎ Haber Merkezi.

Tek pencere, üç ana ekran:
    GirisEkrani  -> oturum aç / hesap oluştur ("Beni hatırla" ile oturum açık kalır)
    HaberEkrani  -> "Seçilen Haberler" ve "Keşfet" sekmeleri (iç sekme)
    AyarEkrani   -> Görünüm / Kaynaklar / Kişiselleştirme / Hesap sekmeleri (iç sekme)

Başlatma:  python ravi.py
"""
import os
import queue
import socket
import sys
import threading
import webbrowser
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from urllib.parse import quote

import feedparser

import depo
import guncelleme
import mizan
from kaynaklar import HABER_ISTASYONU, ISTASYON_BILGI, OZEL_ON_EK

SURUM = "1.1.0"
GERI_BILDIRIM_EPOSTA = "ravi.destek@gmail.com"  # boşsa yalnızca GitHub düğmesi görünür
FEED_BASINA_HABER = 20     # her RSS kaynağından çekilen en fazla haber sayısı

socket.setdefaulttimeout(10)  # cevap vermeyen bir RSS kaynağı akışı kilitlemesin

TEMALAR = {
    "acik": {
        "bg": "#f4f4f4", "kart": "#ffffff", "yazi": "#2c3e50", "soluk": "#7f8c8d",
        "vurgu": "#2980b9", "link": "#3498db", "giris_bg": "#ffffff", "giris_fg": "#2c3e50",
        "tus": "#e0e0e0", "tus_yazi": "#2c3e50", "sekme_bg": "#e8e8e8",
        "yesil": "#27ae60", "turuncu": "#e67e22", "kirmizi": "#c0392b",
    },
    "koyu": {
        "bg": "#14171a", "kart": "#1f2429", "yazi": "#e6e9ec", "soluk": "#8b949e",
        "vurgu": "#58a6ff", "link": "#58a6ff", "giris_bg": "#2a3037", "giris_fg": "#e6e9ec",
        "tus": "#2f363d", "tus_yazi": "#e6e9ec", "sekme_bg": "#1b1f23",
        "yesil": "#2ea043", "turuncu": "#d29922", "kirmizi": "#da3633",
    },
}


def kaynak_yolu(*parca):
    """Logo gibi dosyaları hem normal çalışmada hem PyInstaller paketinde bulur."""
    taban = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(taban, *parca)


def github_issue_url(baslik, govde):
    return (f"https://github.com/{guncelleme.GITHUB_REPO}/issues/new"
            f"?title={quote(baslik)}&body={quote(govde)}")


def mailto_url(adres, konu, govde):
    return f"mailto:{adres}?subject={quote(konu)}&body={quote(govde)}"


def geri_bildirim_govdesi():
    return (f"Sürüm: {SURUM}\nİşletim sistemi: {sys.platform}\n\n"
            f"--- Mesajınızı bu satırın altına yazın ---\n\n")


def tr_kucuk(metin):
    return metin.replace("İ", "i").replace("I", "ı").lower()


# ===================================================================== yardımcılar
class KaydirmaAlani(tk.Frame):
    """Fare tekerleği destekli (Windows + Linux) kaydırılabilir alan. İçerik: self.icerik"""

    def __init__(self, ust, bg):
        super().__init__(ust, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        cubuk = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.icerik = tk.Frame(self.canvas, bg=bg)
        self._pencere = self.canvas.create_window((0, 0), window=self.icerik, anchor="nw")
        self.canvas.configure(yscrollcommand=cubuk.set)
        cubuk.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.icerik.bind("<Configure>",
                         lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._pencere, width=e.width))

        # Tekerlek olayı uygulama genelinde BİR kez bağlanır ve imlecin altındaki
        # kaydırma alanına yönlendirilir (haber ekranında sekme başına bir alan var).
        if not KaydirmaAlani._kurulu:
            KaydirmaAlani._kurulu = True
            for ad in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.bind_all(ad, KaydirmaAlani._genel_tekerlek, add="+")

    def temizle(self):
        """İçeriği baştan kurmak için eski widget'ları atar (arama gibi tam yeniden çizimlerde)."""
        for w in self.icerik.winfo_children():
            w.destroy()

    _kurulu = False

    @staticmethod
    def _genel_tekerlek(olay):
        try:
            w = olay.widget.winfo_containing(olay.x_root, olay.y_root)
        except (tk.TclError, KeyError, AttributeError):
            return
        while w is not None:
            if isinstance(w, KaydirmaAlani):
                w._tekerlek(olay)
                return
            w = getattr(w, "master", None)

    def _tekerlek(self, olay):
        try:
            if self.canvas.yview() == (0.0, 1.0):
                return
        except tk.TclError:
            return
        if olay.num == 4:
            adim = -1
        elif olay.num == 5:
            adim = 1
        else:
            adim = -1 if olay.delta > 0 else 1
        self.canvas.yview_scroll(adim * 3, "units")


class Ekran(tk.Frame):
    """Tüm ekranların ortak tabanı. Renkler her zaman uygulamanın aktif temasından gelir."""

    def __init__(self, app):
        super().__init__(app, bg=app.t["bg"])
        self.app = app

    def kur(self):
        raise NotImplementedError

    def yenile(self):
        """Tema/sekme değişince ekranı yeni durumla baştan çizer."""
        self.configure(bg=self.app.t["bg"])
        for w in self.winfo_children():
            w.destroy()
        self.kur()

    # --- küçük widget fabrikaları
    def etiket(self, ust, metin, boyut=10, kalin=False, renk="yazi", bg=None, **kw):
        return tk.Label(ust, text=metin, font=("Arial", boyut, "bold" if kalin else "normal"),
                        bg=bg or ust.cget("bg"), fg=self.app.t[renk], **kw)

    def dugme(self, ust, metin, komut, renk="tus", **kw):
        t = self.app.t
        fg = t["tus_yazi"] if renk == "tus" else "#ffffff"
        ayar = dict(text=metin, command=komut, bg=t[renk], fg=fg, activebackground=t[renk],
                    activeforeground=fg, relief="flat", bd=0, padx=14, pady=7,
                    cursor="hand2", font=("Arial", 10, "bold"))
        ayar.update(kw)
        return tk.Button(ust, **ayar)

    def girdi(self, ust, gizli=False, genislik=30):
        t = self.app.t
        return tk.Entry(ust, show="*" if gizli else "", width=genislik, bg=t["giris_bg"],
                        fg=t["giris_fg"], insertbackground=t["giris_fg"], relief="flat",
                        highlightthickness=1, highlightbackground=t["soluk"],
                        highlightcolor=t["vurgu"], font=("Arial", 11))

    def kutu(self, ust, metin, var, komut=None, font=("Arial", 10)):
        t = self.app.t
        bg = ust.cget("bg")
        return tk.Checkbutton(ust, text=metin, variable=var, command=komut, bg=bg, fg=t["yazi"],
                              selectcolor=t["giris_bg"], activebackground=bg,
                              activeforeground=t["yazi"], highlightthickness=0, bd=0,
                              font=font, anchor="w")

    def ic_sekme_cubugu(self, ust, sekmeler, aktif, komut, kayit=None):
        """[Sekme1] [Sekme2] ... satırı. sekmeler: [(anahtar, başlık), ...].
        kayit verilirse {anahtar: düğme} ile doldurulur (sonradan renk güncellemek için)."""
        t = self.app.t
        cubuk = tk.Frame(ust, bg=t["sekme_bg"])
        for anahtar, baslik in sekmeler:
            secili = anahtar == aktif
            b = tk.Button(cubuk, text=baslik, relief="flat", bd=0, padx=14, pady=8,
                         cursor="hand2", font=("Arial", 10, "bold"),
                         bg=t["vurgu"] if secili else t["sekme_bg"],
                         fg="#ffffff" if secili else t["soluk"],
                         activebackground=t["vurgu"], activeforeground="#ffffff",
                         command=lambda a=anahtar: komut(a))
            b.pack(side="left")
            if kayit is not None:
                kayit[anahtar] = b
        return cubuk


# ======================================================================= GİRİŞ
class GirisEkrani(Ekran):
    def kur(self):
        t = self.app.t
        kap = tk.Frame(self, bg=t["bg"])
        kap.place(relx=0.5, rely=0.45, anchor="center")

        self.etiket(kap, "RÂVÎ", 54, True, "vurgu").pack()
        self.etiket(kap, "Haber Merkezi", 12, renk="soluk").pack(pady=(0, 24))

        self.etiket(kap, "Kullanıcı adı").pack(anchor="w")
        self.kadi = self.girdi(kap)
        self.kadi.pack(fill="x", pady=(2, 10), ipady=4)

        self.etiket(kap, "Şifre").pack(anchor="w")
        self.sifre = self.girdi(kap, gizli=True)
        self.sifre.pack(fill="x", pady=(2, 10), ipady=4)

        self.hatirla = tk.IntVar(value=1)
        self.kutu(kap, "Beni hatırla (oturum açık kalsın)", self.hatirla).pack(anchor="w")

        self.mesaj = self.etiket(kap, "", 10, True, "kirmizi")
        self.mesaj.pack(pady=10)

        satir = tk.Frame(kap, bg=t["bg"])
        satir.pack(fill="x")
        self.dugme(satir, "OTURUM AÇ", self.oturum_ac, "yesil").pack(
            side="left", expand=True, fill="x", padx=(0, 6))
        self.dugme(satir, "HESAP OLUŞTUR", self.hesap_olustur).pack(
            side="left", expand=True, fill="x")

        self.kadi.bind("<Return>", lambda e: self.sifre.focus_set())
        self.sifre.bind("<Return>", lambda e: self.oturum_ac())
        self.kadi.focus_set()

    def _mesaj_yaz(self, metin, renk):
        self.mesaj.config(text=metin, fg=self.app.t[renk])

    def _alanlar(self):
        kadi, sifre = self.kadi.get().strip(), self.sifre.get().strip()
        if not kadi or not sifre:
            self._mesaj_yaz("Kullanıcı adı ve şifre girin.", "kirmizi")
            return None
        return kadi, sifre

    def oturum_ac(self):
        alanlar = self._alanlar()
        if not alanlar:
            return
        kadi, sifre = alanlar
        durum, _ = depo.giris_kontrol(kadi, sifre)
        if not durum:
            self._mesaj_yaz("Hatalı kullanıcı adı veya şifre!", "kirmizi")
            self.sifre.delete(0, tk.END)
            return
        if self.hatirla.get():
            depo.oturum_kaydet(kadi)
        else:
            depo.oturum_sil()
        self.app.giris_yapildi(kadi)

    def hesap_olustur(self):
        alanlar = self._alanlar()
        if not alanlar:
            return
        kadi, sifre = alanlar
        if depo.kullanici_ekle(kadi, sifre):
            self._mesaj_yaz(f"'{kadi}' hesabı oluşturuldu. Şimdi oturum açabilirsiniz.", "yesil")
        else:
            self._mesaj_yaz("Bu kullanıcı adı zaten kayıtlı!", "kirmizi")


# ======================================================================= HABER
class HaberEkrani(Ekran):
    SEKMELER = [("secilen", "Seçilen Haberler"), ("kesif", "Keşfet")]

    def __init__(self, app):
        super().__init__(app)
        self._nesil = 0
        self.profil = mizan.bos_profil()
        self.havuz = {"secilen": [], "kesif": []}
        self.sayfa = {"secilen": 1, "kesif": 1}
        self.aktif_sekme = "secilen"
        self.alanlar = {}
        self.sekme_dugmeleri = {}

    def kur(self):
        t = self.app.t
        ust = tk.Frame(self, bg=t["kart"])
        ust.pack(fill="x")
        self.etiket(ust, "RÂVÎ", 16, True, "vurgu").pack(side="left", padx=(15, 10), pady=10)
        self.etiket(ust, self.app.kullanici, 10, renk="soluk").pack(side="left")
        self.dugme(ust, "⚙ Ayarlar", lambda: self.app.ekran_goster(AyarEkrani)).pack(
            side="right", padx=(6, 12), pady=8)
        self.yenile_dugmesi = self.dugme(ust, "⟳ Yenile", self.haberleri_getir)
        self.yenile_dugmesi.pack(side="right", pady=8)

        self.sekme_dugmeleri = {}
        sekme_satiri = self.ic_sekme_cubugu(self, self.SEKMELER, self.aktif_sekme, self._sekme_sec,
                                            self.sekme_dugmeleri)
        sekme_satiri.pack(fill="x")

        govde = tk.Frame(self, bg=t["bg"])
        govde.pack(fill="both", expand=True)
        for anahtar, _ in self.SEKMELER:
            alan = KaydirmaAlani(govde, t["bg"])
            self.alanlar[anahtar] = alan
            if anahtar == self.aktif_sekme:
                alan.pack(fill="both", expand=True)

        self.haberleri_getir()

    def _sekme_sec(self, anahtar):
        """Sekmeler arası geçiş SADECE görünürlük değiştirir; ağa yeniden gidilmez.
        Her iki sekmenin verisi zaten haberleri_getir() ile birlikte hesaplanmıştır."""
        if anahtar == self.aktif_sekme:
            return
        self.aktif_sekme = anahtar
        t = self.app.t
        for a, dugme in self.sekme_dugmeleri.items():
            secili = a == anahtar
            dugme.configure(bg=t["vurgu"] if secili else t["sekme_bg"],
                           fg="#ffffff" if secili else t["soluk"])
        for a, alan in self.alanlar.items():
            (alan.pack(fill="both", expand=True) if a == anahtar else alan.pack_forget())

    def _bos_mesaj(self, alan, metin):
        alan.temizle()
        self.etiket(alan.icerik, "SİZİN İÇİN SEÇTİĞİMİZ HABERLER"
                    if self.aktif_sekme == "secilen" else "KAYNAKLARINIZDAN KEŞFEDİN",
                    14, True, pady=20).pack()
        if metin:
            self.etiket(alan.icerik, metin, 11, renk="soluk").pack(pady=30)

    def haberleri_getir(self):
        self._nesil += 1
        nesil = self._nesil
        for anahtar in ("secilen", "kesif"):
            self._bos_mesaj(self.alanlar[anahtar], "Haberler yükleniyor…")
        self.profil = depo.profil_oku(self.app.kullanici)
        if self.profil["ogrenme"] and mizan.sogut(self.profil):
            depo.profil_yaz(self.app.kullanici, self.profil)
        kaynaklar = depo.tercihleri_oku(self.app.kullanici)
        kuyruk = queue.Queue()
        threading.Thread(target=self._arka_plan, args=(kaynaklar, kuyruk), daemon=True).start()
        self.after(150, self._kuyruk_kontrol, nesil, kuyruk)

    @staticmethod
    def _arka_plan(kaynaklar, kuyruk):
        """Ağ işi ayrı iş parçacığında yapılır; pencere donmaz. Arayüze dokunmaz."""
        def cek(k):
            try:
                besleme = feedparser.parse(k["url"])
                return [{"kaynak": k["ad"],
                         "baslik": (h.get("title") or "(başlıksız)").strip(),
                         "link": h.get("link", ""),
                         "tarih": mizan.tarih_zamani(
                             h.get("published_parsed") or h.get("updated_parsed"))}
                        for h in besleme.entries[:FEED_BASINA_HABER]]
            except Exception:
                return []

        with ThreadPoolExecutor(max_workers=8) as havuz:
            sonuc = [h for liste in havuz.map(cek, kaynaklar) for h in liste]
        kuyruk.put(sonuc)

    def _kuyruk_kontrol(self, nesil, kuyruk):
        try:
            if not self.winfo_exists() or nesil != self._nesil:
                return
        except tk.TclError:
            return
        try:
            sonuc = kuyruk.get_nowait()
        except queue.Empty:
            self.after(150, self._kuyruk_kontrol, nesil, kuyruk)
            return
        ogrenme = self.profil["ogrenme"]
        self.havuz = mizan.sec_ve_kesfet(sonuc, self.profil if ogrenme else mizan.bos_profil())
        self.sayfa = {"secilen": 1, "kesif": 1}
        for anahtar in ("secilen", "kesif"):
            self._ciz(anahtar)

    def _ciz(self, anahtar):
        alan = self.alanlar[anahtar]
        havuz = self.havuz[anahtar]
        gosterilen_sayi = self.sayfa[anahtar] * (
            mizan.SAYFA_BOYUTU_SECILEN if anahtar == "secilen" else mizan.SAYFA_BOYUTU_KESIF)
        dilim = havuz[:gosterilen_sayi]

        if not dilim:
            bos = ("Bu sekmede henüz haber yok. Ayarlar'dan kaynak seçtiğinizden emin olun."
                   if anahtar == "secilen" else
                   "Keşfedilecek bir şey yok — tek bir kaynak seçiliyse ya da tüm kaynaklar "
                   "zaten ilginizi çekiyorsa Keşfet boş kalabilir.")
            self._bos_mesaj(alan, bos)
            return

        alan.temizle()
        ogrenme = self.profil["ogrenme"]
        for haber in dilim:
            self._kart_ciz(alan.icerik, haber, ogrenme)

        alt = tk.Frame(alan.icerik, bg=self.app.t["bg"])
        alt.pack(fill="x", pady=(4, 24))
        if len(havuz) > gosterilen_sayi:
            self.dugme(alt, "Daha Fazla Göster", lambda a=anahtar: self._daha_fazla(a)).pack()
        else:
            self.etiket(alt, "Bu kaynaklarda şu an başka haber yok.", 9, renk="soluk").pack()

    def _daha_fazla(self, anahtar):
        self.sayfa[anahtar] += 1
        self._ciz(anahtar)

    def _kart_ciz(self, ust, haber, ogrenme):
        t = self.app.t
        kart = tk.Frame(ust, bg=t["kart"], padx=15, pady=12)
        kart.pack(fill="x", padx=20, pady=6)

        satir = tk.Frame(kart, bg=t["kart"])
        satir.pack(fill="x")
        self.etiket(satir, haber["kaynak"], 8, True, "soluk").pack(side="left")
        if ogrenme:  # "Gizle" bir öğrenme eylemidir; öğrenme kapalıyken gösterilmez
            gizle = self.etiket(satir, "✕ Gizle", 8, True, "soluk")
            gizle.configure(cursor="hand2")
            gizle.pack(side="right")
            gizle.bind("<Button-1>", lambda e, h=haber, k=kart: self._gizle(h, k))

        baslik = self.etiket(kart, haber["baslik"], 11, True,
                             "soluk" if haber["okundu"] else "yazi",
                             wraplength=560, justify="left")
        baslik.pack(anchor="w", pady=(2, 0))

        if haber["link"]:
            git = self.etiket(kart, "Haberi internette gör ➔", 9, True, "link")
            git.configure(cursor="hand2")
            git.pack(anchor="e", pady=(8, 0))
            git.bind("<Button-1>", lambda e, h=haber, b=baslik: self._ac(h, b))

    def _ac(self, haber, baslik_etiketi):
        webbrowser.open(haber["link"])
        if self.profil["ogrenme"] and not haber["okundu"]:
            mizan.ogren(self.profil, haber, "ac")
            depo.profil_yaz(self.app.kullanici, self.profil)
            haber["okundu"] = True
            baslik_etiketi.configure(fg=self.app.t["soluk"])

    def _gizle(self, haber, kart):
        mizan.ogren(self.profil, haber, "gizle")
        depo.profil_yaz(self.app.kullanici, self.profil)
        kart.destroy()


# ======================================================================= AYARLAR
class AyarEkrani(Ekran):
    SEKMELER = [("gorunum", "Görünüm"), ("kaynaklar", "Kaynaklar"),
                ("kisisellestirme", "Kişiselleştirme"), ("hesap", "Hesap")]

    def __init__(self, app, ilk_kurulum=False):
        super().__init__(app)
        self.ilk_kurulum = ilk_kurulum
        kayitli = depo.tercihleri_oku(app.kullanici)
        self.secili = {k["url"] for k in kayitli}
        self.ozel = {k["url"]: k["ad"] for k in kayitli if k["ad"].startswith(OZEL_ON_EK)}
        self.vars = {}
        self.ogrenme = depo.profil_oku(app.kullanici)["ogrenme"]
        self.ogren_var = None
        self.aktif_sekme = "kaynaklar"
        self.genisletilmis = {}
        self.arama_metni = ""

    # --- durum
    def _durumu_topla(self):
        if self.vars:
            self.secili = {url for url, var in self.vars.items() if var.get()}
        if self.ogren_var is not None:
            self.ogrenme = bool(self.ogren_var.get())

    def yenile(self):
        self._durumu_topla()  # sekme/tema değişince işaretlenmiş kutular kaybolmasın
        super().yenile()

    def _var(self, url):
        if url in self.vars:
            return self.vars[url]
        var = tk.IntVar(value=1 if url in self.secili else 0)
        self.vars[url] = var
        return var

    def _toplu(self, degiskenler):
        yeni = 0 if all(v.get() == 1 for v in degiskenler) else 1
        for v in degiskenler:
            v.set(yeni)

    # --- ekran iskeleti
    def kur(self):
        t = self.app.t
        self.vars = {}

        alt = tk.Frame(self, bg=t["bg"])
        alt.pack(side="bottom", fill="x")
        self.dugme(alt, "KAYDET VE HABERLERE DÖN", self._kaydet, "yesil", pady=11).pack(fill="x")

        ust = tk.Frame(self, bg=t["kart"])
        ust.pack(fill="x")
        self.etiket(ust, "⚙ Ayarlar", 16, True, "vurgu").pack(side="left", padx=15, pady=10)
        if not self.ilk_kurulum:
            self.dugme(ust, "Vazgeç", lambda: self.app.ekran_goster(HaberEkrani)).pack(
                side="right", padx=12, pady=8)

        sekme_satiri = self.ic_sekme_cubugu(self, self.SEKMELER, self.aktif_sekme, self._sekme_sec)
        sekme_satiri.pack(fill="x")

        self.govde = KaydirmaAlani(self, t["bg"])
        self.govde.pack(fill="both", expand=True)
        self._sekme_ciz()

    def _sekme_sec(self, anahtar):
        if anahtar == self.aktif_sekme:
            return
        self._durumu_topla()
        self.aktif_sekme = anahtar
        self.yenile()

    def _sekme_ciz(self):
        ic = self.govde.icerik
        if self.ilk_kurulum and self.aktif_sekme == "kaynaklar":
            self.etiket(ic, "Hoş geldiniz! Başlamak için en az bir haber kaynağı seçin.", 11,
                        renk="turuncu", pady=14).pack(anchor="w", padx=20)
        {
            "gorunum": self._cizim_gorunum,
            "kaynaklar": self._cizim_kaynaklar,
            "kisisellestirme": self._cizim_kisisellestirme,
            "hesap": self._cizim_hesap,
        }[self.aktif_sekme](ic)

    # --- GÖRÜNÜM
    def _cizim_gorunum(self, ic):
        self._baslik(ic, "GÖRÜNÜM", "vurgu")
        self.koyu = tk.IntVar(value=1 if self.app.tema_adi == "koyu" else 0)
        self.kutu(ic, "Koyu mod", self.koyu, self._tema_degisti, ("Arial", 11)).pack(
            anchor="w", padx=36, pady=(0, 20))

    def _tema_degisti(self):
        yeni = "koyu" if self.koyu.get() else "acik"
        self.after_idle(self.app.tema_ayarla, yeni)  # kendi düğmesi çalışırken yıkılmasın

    # --- KAYNAKLAR (zengin, daraltılabilir kartlar + arama)
    def _cizim_kaynaklar(self, ic):
        t = self.app.t
        arama_satir = tk.Frame(ic, bg=t["bg"])
        arama_satir.pack(fill="x", padx=20, pady=(14, 10))
        self.etiket(arama_satir, "🔎", 12).pack(side="left", padx=(0, 6))
        self.arama_giris = self.girdi(arama_satir, genislik=28)
        self.arama_giris.insert(0, self.arama_metni)
        self.arama_giris.pack(side="left", fill="x", expand=True, ipady=3)
        self.arama_giris.bind("<KeyRelease>", self._arama_degisti)

        metin = tr_kucuk(self.arama_metni)
        for kaynak_adi, kategoriler in HABER_ISTASYONU.items():
            eslesen_var = (not metin or metin in tr_kucuk(kaynak_adi)
                          or any(metin in tr_kucuk(ad) for ad in kategoriler))
            if metin and not eslesen_var:
                continue
            self._istasyon_karti(ic, kaynak_adi, kategoriler, zorla_ac=bool(metin))

        self._baslik(ic, "ÖZEL KAYNAKLAR", "turuncu", ust_bosluk=20)
        self.ozel_cerceve = tk.Frame(ic, bg=t["bg"])
        self.ozel_cerceve.pack(fill="x")
        for url, ad in self.ozel.items():
            self._ozel_kutu(url, ad)
        self.etiket(ic, "İşareti kaldırdığınız özel kaynaklar kaydedince silinir.", 8,
                    renk="soluk").pack(anchor="w", padx=36)

        form = tk.Frame(ic, bg=t["kart"], padx=14, pady=12)
        form.pack(fill="x", padx=20, pady=12)
        self.etiket(form, "➕ Özel Haber Kaynağı Ekle", 10, True, "turuncu").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.etiket(form, "Kaynak adı:").grid(row=1, column=0, sticky="w")
        self.ad_giris = self.girdi(form, genislik=26)
        self.ad_giris.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        self.etiket(form, "RSS linki:").grid(row=2, column=0, sticky="w")
        self.link_giris = self.girdi(form, genislik=26)
        self.link_giris.grid(row=2, column=1, padx=6, pady=4, sticky="ew")
        form.columnconfigure(1, weight=1)
        self.dugme(form, "Listeye Ekle", self._ozel_ekle, "turuncu").grid(
            row=3, column=1, sticky="e", pady=(6, 0))

    def _istasyon_karti(self, ic, kaynak_adi, tum_kategoriler, zorla_ac):
        t = self.app.t
        simge, aciklama = ISTASYON_BILGI.get(kaynak_adi, ("📰", ""))
        secili_sayi = sum(1 for url in tum_kategoriler.values() if url in self.secili)
        acik = zorla_ac or self.genisletilmis.get(kaynak_adi, False)

        kart = tk.Frame(ic, bg=t["kart"])
        kart.pack(fill="x", padx=20, pady=4)

        baslik = tk.Frame(kart, bg=t["kart"], padx=12, pady=10, cursor="hand2")
        baslik.pack(fill="x")
        ok_etiketi = self.etiket(baslik, "▾" if acik else "▸", 11, True, "soluk", bg=t["kart"])
        ok_etiketi.pack(side="left", padx=(0, 8))
        self.etiket(baslik, simge, 13, bg=t["kart"]).pack(side="left", padx=(0, 8))
        basliklar = tk.Frame(baslik, bg=t["kart"])
        basliklar.pack(side="left", fill="x", expand=True)
        self.etiket(basliklar, kaynak_adi, 11, True, bg=t["kart"]).pack(anchor="w")
        if aciklama:
            self.etiket(basliklar, aciklama, 8, renk="soluk", bg=t["kart"]).pack(anchor="w")
        renk = "vurgu" if secili_sayi else "soluk"
        self.etiket(baslik, f"{secili_sayi}/{len(tum_kategoriler)} seçili", 9, True, renk,
                    bg=t["kart"]).pack(side="right")

        icerik = tk.Frame(kart, bg=t["kart"], padx=12)
        if acik:
            icerik.pack(fill="x", pady=(0, 10))

        def ac_kapa(e=None):
            yeni = not self.genisletilmis.get(kaynak_adi, False)
            self.genisletilmis[kaynak_adi] = yeni
            ok_etiketi.configure(text="▾" if yeni else "▸")
            (icerik.pack(fill="x", pady=(0, 10)) if yeni else icerik.pack_forget())

        for w in (baslik, ok_etiketi, basliklar):
            w.bind("<Button-1>", ac_kapa)

        degiskenler = {url: self._var(url) for url in tum_kategoriler.values()}
        self.dugme(icerik, "Tümünü Seç/Bırak",
                   lambda g=list(degiskenler.values()): self._toplu(g),
                   font=("Arial", 8), padx=8, pady=3).pack(anchor="e", pady=(4, 2))
        for ad, url in tum_kategoriler.items():
            self.kutu(icerik, ad, degiskenler[url]).pack(anchor="w")

    def _arama_degisti(self, olay=None):
        self.arama_metni = self.arama_giris.get()
        self._durumu_topla()
        self.govde.temizle()
        self._sekme_ciz()
        self.arama_giris.focus_set()
        self.arama_giris.icursor(tk.END)

    def _baslik(self, ust, metin, renk, ust_bosluk=10):
        self.etiket(ust, metin, 12, True, renk).pack(anchor="w", padx=20, pady=(ust_bosluk, 2))

    def _ozel_kutu(self, url, ad):
        gorunen = ad[len(OZEL_ON_EK):]
        self.kutu(self.ozel_cerceve, f"⭐ {gorunen} (Özel)", self._var(url),
                  font=("Arial", 10, "italic")).pack(anchor="w", padx=36)

    def _ozel_ekle(self):
        ad, link = self.ad_giris.get().strip(), self.link_giris.get().strip()
        if not ad or not link:
            messagebox.showwarning("Eksik bilgi", "Lütfen tüm alanları doldurun!")
            return
        if not link.lower().startswith(("http://", "https://")):
            messagebox.showwarning("Geçersiz bağlantı",
                                   "RSS adresi http:// veya https:// ile başlamalıdır.")
            return
        if link in self.vars:
            messagebox.showinfo("Zaten var", "Bu kaynak listede zaten mevcut.")
            return
        self.secili.add(link)
        self.ozel[link] = OZEL_ON_EK + ad
        self._ozel_kutu(link, OZEL_ON_EK + ad)
        self.ad_giris.delete(0, tk.END)
        self.link_giris.delete(0, tk.END)

    # --- KİŞİSELLEŞTİRME
    def _cizim_kisisellestirme(self, ic):
        self._baslik(ic, "KİŞİSELLEŞTİRME", "vurgu")
        self.ogren_var = tk.IntVar(value=1 if self.ogrenme else 0)
        self.kutu(ic, "Okuduklarımdan öğren, haberleri ilgi alanıma göre sırala",
                  self.ogren_var).pack(anchor="w", padx=36)
        self.etiket(ic, "Kapalıyken tıklamalarınız kaydedilmez ve sıralamada kullanılmaz.\n"
                        "Öğrenilenler yalnızca bu bilgisayarda kalır.", 8, renk="soluk",
                    justify="left").pack(anchor="w", padx=36, pady=(2, 10))
        self.dugme(ic, "Öğrenilenleri Sıfırla", self._sifirla).pack(anchor="w", padx=36)

    def _sifirla(self):
        if messagebox.askyesno("Öğrenilenleri sıfırla",
                               "İlgi alanlarınız, okuduklarınız ve gizlediğiniz haberler "
                               "silinecek. Emin misiniz?"):
            depo.profil_sifirla(self.app.kullanici)
            messagebox.showinfo("Tamam", "Öğrenilenler silindi.")

    # --- HESAP (sürüm/güncelleme + geri bildirim + çıkış)
    def _cizim_hesap(self, ic):
        self._baslik(ic, "HESAP", "vurgu")
        self.etiket(ic, f"Giriş yapan: {self.app.kullanici}", 10, renk="soluk").pack(
            anchor="w", padx=36, pady=(0, 14))

        self._baslik(ic, "GÜNCELLEME", "vurgu")
        self.etiket(ic, f"Mevcut sürüm: {SURUM}", 10, renk="soluk").pack(anchor="w", padx=36)
        self.dugme(ic, "Güncellemeleri Kontrol Et", self._guncelleme_kontrol_et).pack(
            anchor="w", padx=36, pady=(6, 20))

        self._baslik(ic, "GERİ BİLDİRİM", "vurgu")
        self.etiket(ic, "Bir öneriniz mi var, bir hata mı buldunuz?", 9, renk="soluk").pack(
            anchor="w", padx=36, pady=(0, 6))
        satir = tk.Frame(ic, bg=self.app.t["bg"])
        satir.pack(anchor="w", padx=36, pady=(0, 20))
        self.dugme(satir, "GitHub'da Bildir", self._geri_bildirim_github).pack(
            side="left", padx=(0, 8))
        if GERI_BILDIRIM_EPOSTA:
            self.dugme(satir, "E-posta Gönder", self._geri_bildirim_eposta).pack(side="left")

        self.dugme(ic, "Çıkış Yap", self.app.cikis_yap, "kirmizi").pack(
            anchor="w", padx=36, pady=(0, 28))

    def _guncelleme_kontrol_et(self):
        kuyruk = queue.Queue()

        def isle():
            kuyruk.put(guncelleme.guncelleme_var_mi(SURUM))

        threading.Thread(target=isle, daemon=True).start()
        self.after(150, self._guncelleme_sonucu_bekle, kuyruk)

    def _guncelleme_sonucu_bekle(self, kuyruk):
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        try:
            var, bilgi = kuyruk.get_nowait()
        except queue.Empty:
            self.after(150, self._guncelleme_sonucu_bekle, kuyruk)
            return
        if var:
            if messagebox.askyesno("Yeni Sürüm",
                                   f"{bilgi['baslik']} çıktı. İndirme sayfasını açayım mı?"):
                webbrowser.open(bilgi["url"])
        elif bilgi is None:
            messagebox.showinfo("Güncelleme", "Şu anda güncelleme bilgisine ulaşılamadı. "
                                              "İnternet bağlantınızı kontrol edin.")
        else:
            messagebox.showinfo("Güncelleme", f"RÂVÎ güncel ({SURUM}).")

    def _geri_bildirim_github(self):
        webbrowser.open(github_issue_url("RÂVÎ Geri Bildirim", geri_bildirim_govdesi()))

    def _geri_bildirim_eposta(self):
        webbrowser.open(mailto_url(GERI_BILDIRIM_EPOSTA, "RÂVÎ Geri Bildirim",
                                   geri_bildirim_govdesi()))

    # --- KAYDET
    def _kaydet(self):
        self._durumu_topla()
        final = []
        for kaynak_adi, kategoriler in HABER_ISTASYONU.items():
            for kat_adi, link in kategoriler.items():
                if link in self.secili:
                    final.append({"ad": f"{kaynak_adi} | {kat_adi}", "url": link})
        for link, ad in self.ozel.items():
            if link in self.secili:
                final.append({"ad": ad, "url": link})
        if not final:
            messagebox.showwarning("Seçim yok", "Lütfen en az bir haber kaynağı seçin!")
            return
        depo.tercihleri_kaydet(self.app.kullanici, final)
        profil = depo.profil_oku(self.app.kullanici)
        if profil["ogrenme"] != self.ogrenme:
            profil["ogrenme"] = self.ogrenme
            depo.profil_yaz(self.app.kullanici, profil)
        self.app.ekran_goster(HaberEkrani)


# ======================================================================= UYGULAMA
class RaviUygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RÂVÎ")
        self.geometry("760x840")
        self.minsize(560, 620)
        self._ikon_koy()

        self.tema_adi = depo.ayar_oku("tema", "acik")
        if self.tema_adi not in TEMALAR:
            self.tema_adi = "acik"
        self.t = TEMALAR[self.tema_adi]
        self.configure(bg=self.t["bg"])

        self.kullanici = None
        self.aktif = None

        # Hatırlanan oturum varsa giriş ekranı hiç gösterilmez
        kayitli = depo.oturum_oku()
        if kayitli:
            self.giris_yapildi(kayitli)
        else:
            self.ekran_goster(GirisEkrani)

        self._guncellemeyi_sessizce_kontrol_et()

    def _ikon_koy(self):
        """ravi_logo.ico (Windows) / ravi_logo.png (Linux) varsa pencere simgesi yapar."""
        try:
            if sys.platform.startswith("win"):
                self.iconbitmap(kaynak_yolu("ravi_logo.ico"))
            else:
                self._ikon = tk.PhotoImage(file=kaynak_yolu("ravi_logo.png"))
                self.iconphoto(True, self._ikon)
        except Exception:
            pass

    def ekran_goster(self, sinif, **kw):
        if self.aktif is not None:
            self.aktif.destroy()
        self.aktif = sinif(self, **kw)
        self.aktif.kur()
        self.aktif.pack(fill="both", expand=True)

    def giris_yapildi(self, kullanici):
        self.kullanici = kullanici
        if depo.tercihleri_oku(kullanici):
            self.ekran_goster(HaberEkrani)                      # doğrudan haberler
        else:
            self.ekran_goster(AyarEkrani, ilk_kurulum=True)     # ilk kez: kaynak seçtir

    def cikis_yap(self):
        depo.oturum_sil(self.kullanici)
        self.kullanici = None
        self.ekran_goster(GirisEkrani)

    def tema_ayarla(self, ad):
        self.tema_adi = ad
        self.t = TEMALAR[ad]
        depo.ayar_yaz("tema", ad)
        self.configure(bg=self.t["bg"])
        if self.aktif is not None:
            self.aktif.yenile()

    # --- açılışta sessiz güncelleme kontrolü
    def _guncellemeyi_sessizce_kontrol_et(self):
        atlanan = depo.ayar_oku("atlanan_surum")
        kuyruk = queue.Queue()

        def isle():
            kuyruk.put(guncelleme.guncelleme_var_mi(SURUM))

        threading.Thread(target=isle, daemon=True).start()
        self.after(400, self._guncelleme_sonucu_bekle, kuyruk, atlanan)

    def _guncelleme_sonucu_bekle(self, kuyruk, atlanan):
        try:
            var, bilgi = kuyruk.get_nowait()
        except queue.Empty:
            self.after(400, self._guncelleme_sonucu_bekle, kuyruk, atlanan)
            return
        if not var or bilgi["surum"] == atlanan:
            return  # güncelleme yok, ya da kullanıcı bu sürümü daha önce atladı
        depo.ayar_yaz("atlanan_surum", bilgi["surum"])
        if messagebox.askyesno("Yeni Sürüm",
                               f"{bilgi['baslik']} çıktı. İndirme sayfasını açayım mı?"):
            webbrowser.open(bilgi["url"])


def main():
    RaviUygulama().mainloop()


if __name__ == "__main__":
    main()
