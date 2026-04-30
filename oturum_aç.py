import tkinter as tk
import os
import sys

# 1. HAFIZA BAĞLANTISI
from veri_tabanı import giris_kontrol
from secim import tercih_paneli


# Haber modülü yolu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


try:
    from muhteva.haber import haber_f
except ImportError:
    # Eğer haber_f henüz hazır değilse hata vermemesi için taslak oluşturuyoruz
    def haber_f(tercihler): print(f"Haberler yükleniyor: {tercihler}")


#_________________________________OTURUM_AÇ_____________________________________________
def oturum_ekranı():
    bidayet = tk.Tk()
    bidayet.title("RÂVÎ - Oturum Aç")
    bidayet.geometry("500x250")


    
    # --- SİMGE ---
    try:
        bidayet.iconbitmap(r"C:\Users\sukru\OneDrive\Desktop\RÂVÎ\giriş\ravi_logo.ico") 
    except:
        pass

    # --- KULLANICI ADI BÖLÜMÜ ---
    tk.Label(bidayet, text="Kullanıcı Adı:", font="BOLD 12").place(x=20, y=30)
    kullanıcı_giris = tk.Entry(bidayet) # StringVar yerine doğrudan Entry kullanıyoruz
    kullanıcı_giris.place(x=150, y=32)

    # --- ŞİFRE BÖLÜMÜ ---
    tk.Label(bidayet, text="Şifre:", font="BOLD 12").place(x=20, y=70)
    sifre_giris = tk.Entry(bidayet, show="*")
    sifre_giris.place(x=150, y=72)

    # --- MESAJ ETİKETİ (Önce tanımlıyoruz ki fonksiyon görebilsin) ---
    doğru_yanlis = tk.Label(bidayet, text="", font="Verdana 20 bold")
    doğru_yanlis.place(x=80, y=160)

    # --- GİRİŞ KOMUTU (Fonksiyonun İÇİNDE olmalı) ---
    def giris_komut():
        kadi = kullanıcı_giris.get() 
        sifre = sifre_giris.get()

        print(f"Deneme: '{kadi}' - '{sifre}'") # Terminalden kontrol için

        durum, tercihler = giris_kontrol(kadi, sifre)

        if durum:
            doğru_yanlis.config(text="Giriş Başarılı!", fg="green")
            
            # 1 saniye bekleyip giriş ekranını kapat ve SEÇİM ekranını aç
            bidayet.after(1000, lambda: [bidayet.withdraw(), tercih_paneli(kadi)])
        else:
            doğru_yanlis.config(text="HATALI BİLGİ!", fg="red")
            sifre_giris.delete(0, tk.END)

    # --- BUTON ---
    giris_btn = tk.Button(bidayet, text="SİSTEME GİR", command=giris_komut, width=15, bg="lightgray")
    giris_btn.place(x=150, y=110)

    bidayet.mainloop()

if __name__ == "__main__":
    oturum_ekranı()