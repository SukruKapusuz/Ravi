#!/usr/bin/env python3
"""RÂVÎ Haber Merkezi.

Tek pencere, üç ekran:
    GirisEkrani  -> oturum aç / hesap oluştur ("Beni hatırla" ile oturum açık kalır)
    HaberEkrani  -> seçili kaynaklardan haber akışı (oturum açılınca doğrudan burası gelir)
    AyarEkrani   -> koyu mod, haber kaynakları, çıkış yap

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

import feedparser

import depo
from kaynaklar import HABER_ISTASYONU, OZEL_ON_EK

socket.setdefaulttimeout(10)  # cevap vermeyen bir RSS kaynağı akışı kilitlemesin

TEMALAR = {
    "acik": {
        "bg": "#f4f4f4", "kart": "#ffffff", "yazi": "#2c3e50", "soluk": "#7f8c8d",
        "vurgu": "#2980b9", "link": "#3498db", "giris_bg": "#ffffff", "giris_fg": "#2c3e50",
        "tus": "#e0e0e0", "tus_yazi": "#2c3e50",
        "yesil": "#27ae60", "turuncu": "#e67e22", "kirmizi": "#c0392b",
    },
    "koyu": {
        "bg": "#14171a", "kart": "#1f2429", "yazi": "#e6e9ec", "soluk": "#8b949e",
        "vurgu": "#58a6ff", "link": "#58a6ff", "giris_bg": "#2a3037", "giris_fg": "#e6e9ec",
        "tus": "#2f363d", "tus_yazi": "#e6e9ec",
        "yesil": "#2ea043", "turuncu": "#d29922", "kirmizi": "#da3633",
    },
}


def kaynak_yolu(*parca):
    """Logo gibi dosyaları hem normal çalışmada hem PyInstaller paketinde bulur."""
    taban = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(taban, *parca)


# ===================================================================== yardımcılar
class KaydirmaAlani(tk.Frame):
    """Fare tekerleği destekli (Windows + Linux) kaydırılabilir alan. İçerik: self.icerik"""

    def __init__(self, ust, bg):
        super().__init__(ust, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        cubuk = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.icerik = tk.Frame(self.canvas, bg=bg)
        pencere = self.canvas.create_window((0, 0), window=self.icerik, anchor="nw")
        self.canvas.configure(yscrollcommand=cubuk.set)
        cubuk.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.icerik.bind("<Configure>",
                         lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(pencere, width=e.width))

        self.bind_all("<MouseWheel>", self._tekerlek)   # Windows / macOS
        self.bind_all("<Button-4>", self._tekerlek)     # Linux yukarı
        self.bind_all("<Button-5>", self._tekerlek)     # Linux aşağı
        self.bind("<Destroy>", self._coz)

    def _tekerlek(self, olay):
        if self.canvas.yview() == (0.0, 1.0):
            return
        if olay.num == 4:
            adim = -1
        elif olay.num == 5:
            adim = 1
        else:
            adim = -1 if olay.delta > 0 else 1
        self.canvas.yview_scroll(adim * 3, "units")

    def _coz(self, olay=None):
        if olay is not None and olay.widget is not self:
            return
        try:
            for ad in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.unbind_all(ad)
        except tk.TclError:
            pass


class Ekran(tk.Frame):
    """Tüm ekranların ortak tabanı. Renkler her zaman uygulamanın aktif temasından gelir."""

    def __init__(self, app):
        super().__init__(app, bg=app.t["bg"])
        self.app = app

    def kur(self):
        raise NotImplementedError

    def yenile(self):
        """Tema değişince ekranı yeni renklerle baştan çizer."""
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
    def __init__(self, app):
        super().__init__(app)
        self._nesil = 0

    def kur(self):
        t = self.app.t
        ust = tk.Frame(self, bg=t["kart"])
        ust.pack(fill="x")
        self.etiket(ust, "RÂVÎ", 16, True, "vurgu").pack(side="left", padx=(15, 10), pady=10)
        self.etiket(ust, self.app.kullanici, 10, renk="soluk").pack(side="left")
        self.dugme(ust, "⚙ Ayarlar", lambda: self.app.ekran_goster(AyarEkrani)).pack(
            side="right", padx=(6, 12), pady=8)
        self.dugme(ust, "⟳ Yenile", self.haberleri_getir).pack(side="right", pady=8)

        self.alan = KaydirmaAlani(self, t["bg"])
        self.alan.pack(fill="both", expand=True)
        self.haberleri_getir()

    def _temizle(self, durum_metni=None):
        for w in self.alan.icerik.winfo_children():
            w.destroy()
        self.etiket(self.alan.icerik, "SİZİN İÇİN SEÇTİĞİMİZ HABERLER", 14, True,
                    pady=20).pack()
        if durum_metni:
            self.etiket(self.alan.icerik, durum_metni, 11, renk="soluk").pack(pady=30)

    def haberleri_getir(self):
        self._nesil += 1
        nesil = self._nesil
        self._temizle("Haberler yükleniyor…")
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
                return [(k["ad"], h.get("title", "(başlıksız)"), h.get("link", ""))
                        for h in besleme.entries[:5]]
            except Exception:
                return []

        with ThreadPoolExecutor(max_workers=6) as havuz:
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
        self._kartlari_ciz(sonuc)

    def _kartlari_ciz(self, sonuc):
        t = self.app.t
        self._temizle("" if sonuc else "Haber alınamadı. İnternet bağlantınızı veya kaynak "
                                       "seçimlerinizi (⚙ Ayarlar) kontrol edin.")
        for kaynak, baslik, link in sonuc:
            kart = tk.Frame(self.alan.icerik, bg=t["kart"], padx=15, pady=12)
            kart.pack(fill="x", padx=20, pady=6)
            self.etiket(kart, kaynak, 8, True, "soluk").pack(anchor="w")
            self.etiket(kart, baslik, 11, True, wraplength=560, justify="left").pack(
                anchor="w", pady=(2, 0))
            if link:
                git = self.etiket(kart, "Haberi internette gör ➔", 9, True, "link")
                git.configure(cursor="hand2")
                git.pack(anchor="e", pady=(8, 0))
                git.bind("<Button-1>", lambda e, s=link: webbrowser.open(s))


# ======================================================================= AYARLAR
class AyarEkrani(Ekran):
    def __init__(self, app, ilk_kurulum=False):
        super().__init__(app)
        self.ilk_kurulum = ilk_kurulum
        kayitli = depo.tercihleri_oku(app.kullanici)
        self.secili = {k["url"] for k in kayitli}
        self.ozel = {k["url"]: k["ad"] for k in kayitli if k["ad"].startswith(OZEL_ON_EK)}
        self.vars = {}

    # --- durum
    def _durumu_topla(self):
        if self.vars:
            self.secili = {url for url, var in self.vars.items() if var.get()}

    def yenile(self):
        self._durumu_topla()  # tema değişince işaretlenmiş kutular kaybolmasın
        super().yenile()

    def _var(self, url):
        var = tk.IntVar(value=1 if url in self.secili else 0)
        self.vars[url] = var
        return var

    def _toplu(self, degiskenler):
        yeni = 0 if all(v.get() == 1 for v in degiskenler) else 1
        for v in degiskenler:
            v.set(yeni)

    # --- ekran
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

        alan = KaydirmaAlani(self, t["bg"])
        alan.pack(fill="both", expand=True)
        ic = alan.icerik

        if self.ilk_kurulum:
            self.etiket(ic, "Hoş geldiniz! Başlamak için en az bir haber kaynağı seçin.", 11,
                        renk="turuncu", pady=14).pack(anchor="w", padx=20)

        # -- görünüm
        self._baslik(ic, "GÖRÜNÜM", "vurgu")
        self.koyu = tk.IntVar(value=1 if self.app.tema_adi == "koyu" else 0)
        self.kutu(ic, "Koyu mod", self.koyu, self._tema_degisti, ("Arial", 11)).pack(
            anchor="w", padx=36)

        # -- haber kaynakları
        self._baslik(ic, "HABER KAYNAKLARI", "vurgu", ust_bosluk=22)
        for kaynak_adi, kategoriler in HABER_ISTASYONU.items():
            satir = tk.Frame(ic, bg=t["bg"])
            satir.pack(fill="x", padx=20, pady=(12, 2))
            self.etiket(satir, kaynak_adi.upper(), 11, True, "vurgu").pack(side="left")
            grup = []
            for kat_adi, link in kategoriler.items():
                var = self._var(link)
                grup.append(var)
                self.kutu(ic, kat_adi, var).pack(anchor="w", padx=36)
            self.dugme(satir, "Tümünü Seç/Bırak", lambda g=grup: self._toplu(g),
                       font=("Arial", 8), padx=8, pady=3).pack(side="right")

        # -- özel kaynaklar
        self._baslik(ic, "ÖZEL KAYNAKLAR", "turuncu", ust_bosluk=18)
        self.ozel_cerceve = tk.Frame(ic, bg=t["bg"])
        self.ozel_cerceve.pack(fill="x")
        for url, ad in self.ozel.items():
            self._ozel_kutu(url, ad)
        self.etiket(ic, "İşareti kaldırdığınız özel kaynaklar kaydedince silinir.", 8,
                    renk="soluk").pack(anchor="w", padx=36)

        form = tk.LabelFrame(ic, text=" ➕ Özel Haber Kaynağı Ekle ", bg=t["bg"], fg=t["turuncu"],
                             padx=10, pady=10, font=("Arial", 10, "bold"))
        form.pack(fill="x", padx=20, pady=12)
        self.etiket(form, "Kaynak adı:").grid(row=0, column=0, sticky="w")
        self.ad_giris = self.girdi(form, genislik=26)
        self.ad_giris.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        self.etiket(form, "RSS linki:").grid(row=1, column=0, sticky="w")
        self.link_giris = self.girdi(form, genislik=26)
        self.link_giris.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        form.columnconfigure(1, weight=1)
        self.dugme(form, "Listeye Ekle", self._ozel_ekle, "turuncu").grid(
            row=2, column=1, sticky="e", pady=(6, 0))

        # -- hesap
        self._baslik(ic, "HESAP", "vurgu", ust_bosluk=18)
        self.etiket(ic, f"Giriş yapan: {self.app.kullanici}", 10, renk="soluk").pack(
            anchor="w", padx=36)
        self.dugme(ic, "Çıkış Yap", self.app.cikis_yap, "kirmizi").pack(
            anchor="w", padx=36, pady=(8, 28))

    def _baslik(self, ust, metin, renk, ust_bosluk=10):
        self.etiket(ust, metin, 12, True, renk).pack(anchor="w", padx=20, pady=(ust_bosluk, 2))

    def _ozel_kutu(self, url, ad):
        gorunen = ad[len(OZEL_ON_EK):]
        self.kutu(self.ozel_cerceve, f"⭐ {gorunen} (Özel)", self._var(url),
                  font=("Arial", 10, "italic")).pack(anchor="w", padx=36)

    # --- olaylar
    def _tema_degisti(self):
        yeni = "koyu" if self.koyu.get() else "acik"
        self.after_idle(self.app.tema_ayarla, yeni)  # kendi düğmesi çalışırken yıkılmasın

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
        self.app.ekran_goster(HaberEkrani)


# ======================================================================= UYGULAMA
class RaviUygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RÂVÎ")
        self.geometry("720x820")
        self.minsize(520, 600)
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


def main():
    RaviUygulama().mainloop()


if __name__ == "__main__":
    main()
