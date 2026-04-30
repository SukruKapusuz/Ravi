

import tkinter as tk
#kütüphaneyi çağırır tk diye isim takar

from oturum_aç import *

from veri_tabanı import kullanici_ekle


import sys
import os
import time


# Bir üst dizini Python'un arama yoluna ekler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

mevcut_dizin = os.path.dirname(__file__)
ikon_yolu = os.path.join(mevcut_dizin, "ravi_logo.ico")






hesap_ac = tk.Tk()
#ekran oluşturur
hesap_ac.title("RÂVÎ")
#görünür ser levha koyar
hesap_ac.geometry("500x400")
#boyutlandırır



# --- SİMGE EKLEME SATIRI ---
try:
    hesap_ac.iconbitmap(ikon_yolu)
except:
    pass # Dosya yoksa sessizce devam eder
# _______________________________________________________

#_______________________________proje ismi__________________________________
ser_levha = tk.Label(text="RÂVÎ", font="Verdana 60 normal")
ser_levha.place(x=135,y=20)
#___________________________________________________________________

#__________________________________________hesap-oluştur______________________
yönlendirme = tk.Label(text="Hesabınız yok ise buradan hesap açınız:", font="Verdana 10 normal")
yönlendirme.place(x=15,y=120)
#____________________________________________________________________________




#________________İsim___________________
isim = tk.Label(text="KULLANICI ADI:")
isim.place(x=20,y=150)

isim_kayıd = tk.StringVar()
isim_girisi = tk.Entry(textvariable = isim_kayıd)
isim_girisi.place(x=130,y=150)
#______________________________________________

#__________________sifre______________________
Sifre = tk.Label(text="Şifre GİRİSİ:")
Sifre.place(x=20,y=175)

sifre_kayıd= tk.StringVar()
Sifre_girisi = tk.Entry(textvariable=sifre_kayıd)
Sifre_girisi.place(x=130,y=175)
#_____________________________________________




#_______________________________________kaydol_tuşu___________________________________
def kaydol_komutu():
    xget = sifre_kayıd.get()
    yget = isim_kayıd.get()
    
    if len(yget) > 0 and len(xget) > 0:
        # YENİ: Bilgileri kalıcı olarak dosyaya yazar
        kullanici_ekle(yget, xget) 
        print(f"Sistem: {yget} kullanıcısı RÂVÎ hafızasına kaydedildi.")
    else:
        #ana pencere değil ikaz penceresi o yüzden tk değil toplevel 
        galat_ikazı = tk.Toplevel()
        galat_ikazı.title("İKAZ")
        galat_ikazı.geometry("250x100")

        
        # --- SİMGE EKLEME SATIRI ---
        
        try:
            galat_ikazı.iconbitmap(ikon_yolu)
        except:
            pass # Dosya yoksa sessizce devam eder



        ikaz_metni = tk.Label(galat_ikazı, text="Eksik bilgi girdiniz!", fg="red",font="Verdana 15 bold")
        ikaz_metni.pack(expand=True) # Pencerenin ortasına yerleştirir

        # 2 saniye (2000 milisaniye) sonra pencereyi otomatik kapat
        galat_ikazı.after(2000, galat_ikazı.destroy)

hesap1 = tk.Button(text="Hesabı kaydet",command=kaydol_komutu)
hesap1.place(x=150,y=200)
#_____________________________________________________________________________________________________________________________






#_________________________________________oturum_aç______________________
oturum = tk.Label(text="Hesabınız var ise buradan oturum açınız:", font="Verdana 10 normal")
oturum.place(x=15,y=225)
#____________________________________________________________________________

def oturum_komudu():
    # 1. Ana pencereyi (bidayet) gizle
    hesap_ac.withdraw() 
    
    # 2. Yeni ekranı aç
    oturum_ekranı()



oturum_ac = tk.Button(text="OTURUM AÇ",command=oturum_komudu)
oturum_ac.place(x=150,y=250)












hesap_ac.mainloop()
#görünür yapılır