import tkinter as tk         # Pencereler, butonlar ve görsel her şey için
import json                  # Kullanıcı tercihlerini (ne izlemek istiyor?) kaydetmek için
import webbrowser            # Habere tıklandığında kullanıcının tarayıcısını açmak için
import feedparser            # İnternetteki RSS (haber) kodlarını okuyup başlığa çevirmek için
from tkinter import messagebox # Hata veya uyarı mesaj kutuları için
from veri_tabanı import verileri_oku # Kullanıcı listesini kontrol eden kendi fonksiyonun

# --- 1. HABER KAYNAKLARI (RSS HAVUZU) ---
# Bu sözlükler (dict), hangi kanalın hangi internet adresinden yayın yaptığını tutar.

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

# Teknoloji sitelerini birleştirme (** operatörü ile iki sözlüğü birleştirir)
donanım_haber = {"Donanım Haber": "https://www.donanimhaber.com/rss/tum/"}
shiftdelete = {"ShiftDelete": "https://shiftdelete.net/feed"}
teknoloji_birlesik = {**shiftdelete, **donanım_haber}

# Ana İstasyon: Tüm kanalları tek bir çatı altında toplar.
haber_istasyonu = {
    "NTV": ntv_tam_liste,
    "TRT": trt_haber_tam_liste, 
    "CNN": cnn_turk_derin_arsiv,
    "BBC": bbc_derin_arsiv,
    "Teknoloji": teknoloji_birlesik
}

# --- 2. SEÇİM PANELİ (KULLANICININ GAZETESİNİ OLUŞTURDUĞU YER) ---

def tercih_paneli(kullanici_adi):
    # Toplevel: Giriş ekranının üzerinde yeni bir pencere açar.
    pencere = tk.Toplevel()
    pencere.title(f"RÂVÎ Haber Merkezi - {kullanici_adi}")
    pencere.geometry("550x750")

    # Kaydırma Çubuğu (Scrollbar) Mekanizması: Liste çok uzun olursa aşağı kaysın diye.
    ana_frame = tk.Frame(pencere)
    ana_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(ana_frame) # Üzerine yazı/buton koyabildiğimiz kaydırılabilir alan.
    v_scrollbar = tk.Scrollbar(ana_frame, orient="vertical", command=canvas.yview)
    scroll_icerik = tk.Frame(canvas) # Kutucukların asıl dizileceği iç katman.

    # İçerik değiştikçe kaydırma alanının boyutunu otomatik hesaplar.
    scroll_icerik.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_icerik, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    v_scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    secim_kutulari = {} # Kullanıcının işaretlediği "IntVar" ve "Link" çiftini saklar.

    # Grup Seçim Fonksiyonu: "Tümünü Seç" butonuna basınca o kanalın tüm kutularını doldurur.
    def hepsini_sec_grup(degiskenler):
        # Eğer hepsi seçiliyse 0 (boşalt), biri bile boşsa 1 (doldur) yapar.
        yeni_durum = 0 if all(var.get() == 1 for var in degiskenler) else 1
        for var in degiskenler:
            var.set(yeni_durum)

    # DİNAMİK LİSTELEME: 'haber_istasyonu'ndaki her şeyi ekrana kutucuk olarak basar.
    for kaynak_adi, kategoriler in haber_istasyonu.items():
        baslik_frame = tk.Frame(scroll_icerik)
        baslik_frame.pack(fill="x", padx=10, pady=(15, 5))

        # Kanal Başlığı (Örn: NTV, BBC)
        tk.Label(baslik_frame, text=kaynak_adi.upper(), font="Arial 12 bold", fg="#2980b9").pack(side="left")
        
        grup_vars = [] # O kanala ait kutucukları (0/1 durumlarını) burada toplarız.
        for kat_adi, rss_link in kategoriler.items():
            var = tk.IntVar() # Kutunun dolu mu boş mu olduğunu anlık takip eden değişken.
            grup_vars.append(var)
            
            # Checkbutton: İşaretleme kutusu.
            cb = tk.Checkbutton(scroll_icerik, text=kat_adi, variable=var, font="Arial 10")
            cb.pack(anchor="w", padx=30)
            
            # Hafızaya al: "Kanal | Kategori" ismine karşılık gelen (değişken, link) verisini sakla.
            secim_kutulari[f"{kaynak_adi} | {kat_adi}"] = (var, rss_link)

        # "Tümünü Seç" Butonu: Sadece o kanalın grubuna (grup_vars) hükmeder.
        btn = tk.Button(baslik_frame, text="Tümünü Seç", font="Arial 8", 
                        command=lambda v=grup_vars: hepsini_sec_grup(v))
        btn.pack(side="right")

    # --- 3. KAYDET VE HABER EKRANINI AÇ ---
    def kaydet_ve_baslat():
        final_secimler = [] # JSON dosyasına yazılacak olan liste.
        secilen_linkler = [] # İnternetten çekilecek olan saf link listesi.
        
        # Kullanıcının 1 (seçili) yaptığı her şeyi ayıkla.
        for etiket, (var, link) in secim_kutulari.items():
            if var.get() == 1:
                final_secimler.append({"ad": etiket, "url": link})
                secilen_linkler.append(link)

        # JSON Kayıt İşlemi: Kullanıcının profilini günceller.
        veriler = verileri_oku()
        if kullanici_adi in veriler:
            veriler[kullanici_adi]["tercihler"] = final_secimler
            with open("kullanicilar.json", "w", encoding="utf-8") as f:
                json.dump(veriler, f, ensure_ascii=False, indent=4)
        
        # Eğer en az bir link seçildiyse;
        if secilen_linkler:
            pencere.destroy() # Seçim ekranını kapat.
            haber_sun_ekrani(secilen_linkler) # Haberleri gösterecek olan ana ekrana git.
        else:
            messagebox.showwarning("Uyarı", "Lütfen en az bir haber kategorisi seçin!")

    # Ana Onay Butonu: Yeşil renkli, dikkat çekici ve en altta.
    tk.Button(pencere, text="TERCİHLERİ KAYDET VE HABERLERİ GETİR 🚀", command=kaydet_ve_baslat, 
              bg="#27ae60", fg="white", font="Arial 11 bold", pady=10).pack(fill="x")

# --- 4. 📺 HABERLERİ EKRANDA SUNAN ANA PENCERE (GAZETE EKRANI) ---

def haber_sun_ekrani(linkler):
    # Toplevel: Haberleri ayrı bir temiz pencerede gösterir.
    haber_pencere = tk.Toplevel()
    haber_pencere.title("RÂVÎ - Haber Akışı")
    haber_pencere.geometry("800x850")
    haber_pencere.configure(bg="#f4f4f4")

    # Kaydırma alanı (Yüzlerce haber gelse bile ekranın aşağı kayabilmesini sağlar)
    h_canvas = tk.Canvas(haber_pencere, bg="#f4f4f4", highlightthickness=0)
    h_scroll = tk.Scrollbar(haber_pencere, orient="vertical", command=h_canvas.yview)
    haber_liste_frame = tk.Frame(h_canvas, bg="#f4f4f4")

    haber_liste_frame.bind("<Configure>", lambda e: h_canvas.configure(scrollregion=h_canvas.bbox("all")))
    
    # Haberlerin genişliğinin pencereye tam sığması için Canvas içine pencere oluşturur.
    canvas_window = h_canvas.create_window((0, 0), window=haber_liste_frame, anchor="nw")

    # Pencere boyutu değiştikçe haber kartlarının genişliğini otomatik ayarla.
    def adjust_width(event):
        h_canvas.itemconfig(canvas_window, width=event.width)
    h_canvas.bind('<Configure>', adjust_width)

    h_canvas.configure(yscrollcommand=h_scroll.set)
    h_scroll.pack(side="right", fill="y")
    h_canvas.pack(side="left", fill="both", expand=True)

    # --- HABERLERİ İNTERNETTEN ÇEKME VE BASMA ---
    for url in linkler:
        try:
            besleme = feedparser.parse(url) # RSS linkini indir ve içeriği ayıkla.
            
            for haber in besleme.entries[:5]: # Her kategoriden en güncel 5 haberi çek.
                # Haber Kartı Tasarımı (Beyaz, temiz bir kutucuk)
                kart = tk.Frame(haber_liste_frame, bg="white", bd=1, relief="flat", pady=15, padx=15)
                kart.pack(fill="x", padx=30, pady=10)

                # Başlık: Kalın ve koyu renkli, 700 pikselden sonra alt satıra geçer.
                baslik = tk.Label(kart, text=haber.title, font="Arial 11 bold", 
                                  wraplength=650, justify="left", bg="white", fg="#2c3e50")
                baslik.pack(anchor="w")

                # "Habere Git" Butonu/Link Etiketi
                link_etiket = tk.Label(kart, text="Devamını Oku ➔", fg="#3498db", 
                                       cursor="hand2", bg="white", font="Arial 9 bold")
                link_etiket.pack(anchor="e", pady=(10, 0))
                
                # Tıklama Olayı: Kullanıcı yazıya bastığında tarayıcıda ilgili link açılır.
                link_etiket.bind("<Button-1>", lambda e, s=haber.link: webbrowser.open(s))
        
        except Exception as e:
            # İnternet kesilirse veya link çalışmazsa programın çökmesini engeller, hata yazar.
            print(f"Haber çekilemedi: {url} -> Hata: {e}")

    haber_pencere.mainloop()