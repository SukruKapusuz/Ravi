import tkinter as tk  # Pencereler, butonlar ve kutucuklar için ana kütüphane
import json           # Kullanıcı seçimlerini (tercihleri) dosyaya kalıcı yazmak için
import os             # Bilgisayardaki dosya yollarını (ikon, logo) hatasız bulmak için
import sys            # Python'ın 'muhteva' gibi yan klasörlere ulaşabilmesi için
import webbrowser     # Habere tıklandığında kullanıcının varsayılan tarayıcısını açmak için
import feedparser     # İnternetteki karmaşık RSS kodlarını okuyup başlığa çeviren motor
from veri_tabanı import verileri_oku  # Kayıtlı kullanıcıları kontrol eden senin fonksiyonun

# --- 1. SİSTEM AYARLARI ---
# Bu satır, Python'a "Şu an içinde bulunduğun klasöre de bak, dosyaları kaybetme" talimatı verir.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- 2. SABİT HABER KAYNAKLARI (RSS HAVUZU) ---
# Sözlük yapısı: {"Kategori Adı": "İnternet Adresi"} şeklinde çalışır.

ntv_tam_liste = {
    "Son Dakika": "https://www.ntv.com.tr/gundem.rss",
    "Türkiye": "https://www.ntv.com.tr/turkiye.rss",
    "Dünya": "https://www.ntv.com.tr/dunya.rss",
    "Ekonomi": "https://www.ntv.com.tr/ekonomi.rss",
    "Teknoloji": "https://www.ntv.com.tr/teknoloji.rss",
    "Sağlık": "https://www.ntv.com.tr/saglik.rss",
    "Spor": "https://www.ntv.com.tr/spor.rss",
    "Otomobil": "https://www.ntv.com.tr/otomobil.rss"
}

trt_haber_tam_liste = {
    "Manşetler": "https://www.trthaber.com/manset_articles.rss",
    "Son Dakika": "https://www.trthaber.com/sondakika_articles.rss",
    "Gündem": "https://www.trthaber.com/gundem_articles.rss",
    "Ekonomi": "https://www.trthaber.com/ekonomi_articles.rss",
    "Spor": "https://www.trthaber.com/spor_articles.rss"
}

cnn_turk_derin_arsiv = {
    "Günün Haberleri": "https://www.cnnturk.com/feed/rss/all/news",
    "Dünya": "https://www.cnnturk.com/feed/rss/dunya/news",
    "Teknoloji": "https://www.cnnturk.com/feed/rss/teknoloji/news"
}

bbc_derin_arsiv = {
    "Manşetler": "https://feeds.bbci.co.uk/turkce/rss.xml",
    "Türkiye": "https://feeds.bbci.co.uk/turkce/turkiye/rss.xml",
    "Bilim": "https://feeds.bbci.co.uk/turkce/bilim/rss.xml"
}

# Teknoloji sitelerini birleştirme (** operatörü iki sözlüğü tek bir pakete dönüştürür)
donanım_haber = {"Donanım Haber": "https://www.donanimhaber.com/rss/tum/"}
shiftdelete = {"ShiftDelete": "https://shiftdelete.net/feed"}
teknoloji_birlesik = {**shiftdelete, **donanım_haber}

# Ana İstasyon: Tüm kanalları tek bir çatı (sözlük) altında toplar.
haber_istasyonu = {
    "NTV": ntv_tam_liste,
    "TRT": trt_haber_tam_liste, 
    "CNN": cnn_turk_derin_arsiv,
    "BBC": bbc_derin_arsiv,
    "Teknoloji": teknoloji_birlesik
}

# --- 3. SEÇİM PANELİ FONKSİYONU ---
def tercih_paneli(kullanici_adi):
    # Toplevel: Giriş ekranının üzerine açılan, ona bağlı yeni bir pencere oluşturur.
    pencere = tk.Toplevel()
    pencere.title(f"RÂVÎ Haber Merkezi - {kullanici_adi}")
    pencere.geometry("550x850") 

    # --- SİMGE AYARI ---
    try:
        # Programın çalıştığı klasörü bulur ve logo dosyasını pencereye takar.
        dizin = os.path.dirname(os.path.abspath(__file__))
        ikon_yolu = os.path.join(dizin, "giriş", "ravi_logo.ico")
        pencere.iconbitmap(ikon_yolu)
    except:
        pass # Logo bulunamazsa hata verme, devam et.

    # --- KAYDIRMA ÇUBUĞU (SCROLLBAR) MEKANİZMASI ---
    ana_frame = tk.Frame(pencere) # Tüm pencereyi kaplayan ana çerçeve.
    ana_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(ana_frame, highlightthickness=0) # Üzerinde kaydırma yapılan tuval.
    v_scrollbar = tk.Scrollbar(ana_frame, orient="vertical", command=canvas.yview)
    scroll_icerik = tk.Frame(canvas) # Kutucukların asıl dizildiği iç katman.

    # İçerik eklendikçe kaydırma alanının uzunluğunu (scrollregion) otomatik ayarlar.
    scroll_icerik.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_icerik, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    v_scrollbar.pack(side="right", fill="y") # Çubuğu sağa yasla.
    canvas.pack(side="left", fill="both", expand=True) # Tuvali sola yay.

    # secim_kutulari: Kullanıcının hangi kutuyu tıkladığını hafızada tutan depo.
    secim_kutulari = {} 

    # --- TOPLU SEÇİM FONKSİYONU ---
    def hepsini_sec_grup(degiskenler):
        # Hepsi seçiliyse boşalt (0), biri bile boşsa doldur (1) mantığıyla çalışır.
        yeni_durum = 0 if all(var.get() == 1 for var in degiskenler) else 1
        for var in degiskenler:
            var.set(yeni_durum) # Grubun tüm kutularını güncelle.

    # --- KANALLARI EKRANA DİZME (DÖNGÜ) ---
    for kaynak_adi, kategoriler in haber_istasyonu.items():
        baslik_frame = tk.Frame(scroll_icerik)
        baslik_frame.pack(fill="x", padx=10, pady=(15, 5))

        # Kanal Başlığı (Örn: TRT, CNN)
        tk.Label(baslik_frame, text=kaynak_adi.upper(), font="Arial 12 bold", fg="#2980b9").pack(side="left")
        
        grup_vars = [] # O kanala ait kutucukların durum değişkenlerini tutar.
        for kat_adi, rss_link in kategoriler.items():
            var = tk.IntVar() # Kutunun dolu/boş durumunu anlık izleyen Python objesi.
            grup_vars.append(var)
            
            # Checkbutton: Kullanıcının tıklayabildiği kare kutucuk.
            cb = tk.Checkbutton(scroll_icerik, text=kat_adi, variable=var, font="Arial 10")
            cb.pack(anchor="w", padx=30)
            
            # Belleğe kaydet: "Kanal | Kategori" anahtarına karşı (durum, link) ikilisini sakla.
            secim_kutulari[f"{kaynak_adi} | {kat_adi}"] = (var, rss_link)

        # "Tümünü Seç" Butonu: Sadece o kanalın altındaki kutuları etkiler.
        btn = tk.Button(baslik_frame, text="Tümünü Seç/Bırak", font="Arial 8", 
                        command=lambda v=grup_vars: hepsini_sec_grup(v))
        btn.pack(side="right")

    # --- 4. ÖZEL RSS KAYNAĞI EKLEME PANELİ ---
    ozel_ekle_frame = tk.LabelFrame(scroll_icerik, text=" ➕ Özel Haber Kaynağı Ekle ", padx=10, pady=10, fg="#e67e22")
    ozel_ekle_frame.pack(fill="x", padx=20, pady=20)

    # Entry: Kullanıcının metin girişi yapabileceği boş kutular.
    tk.Label(ozel_ekle_frame, text="Kaynak Adı:").grid(row=0, column=0, sticky="w")
    kaynak_adi_ent = tk.Entry(ozel_ekle_frame, width=20)
    kaynak_adi_ent.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ozel_ekle_frame, text="RSS Linki:").grid(row=1, column=0, sticky="w")
    rss_link_ent = tk.Entry(ozel_ekle_frame, width=40)
    rss_link_ent.grid(row=1, column=1, padx=5, pady=5)

    def ozel_kaynak_ekle():
        ad = kaynak_adi_ent.get() # Giriş kutusundaki ismi al.
        link = rss_link_ent.get() # Giriş kutusundaki linki al.
        if ad and link:
            yeni_etiket = f"Özel | {ad}"
            var = tk.IntVar(value=1) # Yeni eklenen kaynağı direkt "seçili" işaretle.
            # Ekrana anında yeni bir kutucuk basar:
            cb = tk.Checkbutton(scroll_icerik, text=f"⭐ {ad} (Özel)", variable=var, font="Arial 10 italic")
            cb.pack(anchor="w", padx=30)
            # Sistemin bu yeni linki tanıması için listeye ekle:
            secim_kutulari[yeni_etiket] = (var, link)
            # Kutuları temizle:
            kaynak_adi_ent.delete(0, tk.END)
            rss_link_ent.delete(0, tk.END)
        else:
            tk.messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun!")

    tk.Button(ozel_ekle_frame, text="Kaynağı Listeye Ekle", command=ozel_kaynak_ekle, bg="#e67e22", fg="white").grid(row=2, column=1, sticky="e", pady=5)

    # --- 5. KAYDET VE BAŞLAT FONKSİYONU ---
    def kaydet_ve_baslat():
        final_secimler = [] # JSON dosyasına gidecek olan (Etiket + URL) listesi.
        secilen_linkler = [] # Haber motorunun okuyacağı saf link listesi.
        
        # Hafızadaki tüm kutuları tara, hangileri '1' (seçili) ise onları ayıkla.
        for etiket, (var, link) in secim_kutulari.items():
            if var.get() == 1:
                final_secimler.append({"ad": etiket, "url": link})
                secilen_linkler.append(link)

        # Eğer hiçbir şey seçilmemişse uyarı ver ve dur.
        if not secilen_linkler:
            tk.messagebox.showwarning("Seçim Yok", "Lütfen en az bir haber kategorisi seçin!")
            return

        # --- JSON VERİTABANI KAYDI ---
        try:
            veriler = verileri_oku() # Kullanıcı verilerini oku.
            if kullanici_adi in veriler:
                # Kullanıcının profilindeki 'tercihler' kısmını yeni listeyle güncelle.
                veriler[kullanici_adi]["tercihler"] = final_secimler
                # Dosyayı aç ve üzerine kaydet (indent=4 kodu okunabilir yapar).
                with open("kullanicilar.json", "w", encoding="utf-8") as f:
                    json.dump(veriler, f, ensure_ascii=False, indent=4)
                print(f"RÂVÎ: {len(final_secimler)} kaynak kaydedildi.")
        except Exception as e:
            print(f"Veri kaydı sırasında hata oluştu: {e}")

        # Seçim ekranını kapat.
        pencere.destroy()
        
        # --- HABERLERİ GETİRME ---
        try:
            # Önce bu dosyanın altındaki 'haber_sun_ekrani' fonksiyonuna bakar.
            if 'haber_sun_ekrani' in globals():
                haber_sun_ekrani(secilen_linkler)
            else:
                # Eğer o fonksiyon yoksa dışarıdaki 'haber_f' fonksiyonunu çağırır.
                from muhteva.haber import haber_f
                haber_f(secilen_linkler)
        except Exception as e:
            print(f"Haber bülteni açılırken teknik bir hata oluştu: {e}")

    # --- ANA ONAY BUTONU ---
    tk.Button(pencere, text="TERCİHLERİ KAYDET VE HABERLERİ GETİR ", command=kaydet_ve_baslat, 
              bg="#27ae60", fg="white", font="Arial 11 bold", pady=10).pack(fill="x")

    pencere.grab_set() # Kullanıcı bu pencereyi kapatmadan arkadakilere dokunamaz.

# --- 6. 📺 HABER SUNUM EKRANI (MODERN TASARIM) ---
def haber_sun_ekrani(linkler):
    # Haberleri gösteren ana pencere.
    h_pencere = tk.Toplevel()
    h_pencere.title("RÂVÎ - Güncel Haber Akışı")
    h_pencere.geometry("700x850")
    h_pencere.configure(bg="#f4f4f4") # Hafif gri, göz yormayan arka plan.

    h_canvas = tk.Canvas(h_pencere, bg="#f4f4f4", highlightthickness=0)
    h_scroll = tk.Scrollbar(h_pencere, orient="vertical", command=h_canvas.yview)
    h_frame = tk.Frame(h_canvas, bg="#f4f4f4")

    # Pencere içindeki içerik değiştikçe kaydırma alanını genişlet.
    h_frame.bind("<Configure>", lambda e: h_canvas.configure(scrollregion=h_canvas.bbox("all")))
    h_canvas.create_window((0, 0), window=h_frame, anchor="nw", width=680)
    h_canvas.configure(yscrollcommand=h_scroll.set)

    h_scroll.pack(side="right", fill="y")
    h_canvas.pack(side="left", fill="both", expand=True)

    # Başlık Paneli
    tk.Label(h_frame, text="SİZİN İÇİN SEÇTİĞİMİZ HABERLER", font="Arial 14 bold", 
             bg="#f4f4f4", fg="#2c3e50", pady=20).pack()

    # --- HABER ÇEKME VE KARTLARA DİZME ---
    for url in linkler:
        try:
            besleme = feedparser.parse(url) # Linke bağlan ve veriyi çek.
            for haber in besleme.entries[:5]: # Her linkten en yeni 5 haberi al.
                # Haber Kartı: Beyaz, gölgeli kutucuk görünümü.
                kart = tk.Frame(h_frame, bg="white", bd=1, relief="flat", padx=15, pady=15)
                kart.pack(fill="x", padx=20, pady=10)

                # Haber Başlığı: 600 piksel genişlikten sonra alt satıra geçer.
                tk.Label(kart, text=haber.title, font="Arial 11 bold", wraplength=600, 
                         justify="left", bg="white", fg="#2c3e50").pack(anchor="w")
                
                # "Devamını Oku" Linki: El işareti (hand2) çıkarır.
                link_btn = tk.Label(kart, text="Haberi İnternette Gör ➔", fg="#3498db", 
                                    cursor="hand2", bg="white", font="Arial 9 bold")
                link_btn.pack(anchor="e", pady=(10,0))
                # Tıklayınca webbrowser kütüphanesi ile linki açar:
                link_btn.bind("<Button-1>", lambda e, s=haber.link: webbrowser.open(s))
        except:
            # İnternet yoksa veya link hatalıysa o kaynağı atla.
            continue

    h_pencere.mainloop()