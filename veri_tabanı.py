

import os
import json

#----------------------------------------------okuma yazma (hafıza)------------------
def verileri_oku():
    # 1. Kontrol: Dosya yerinde mi?
    if not os.path.exists("kullanicilar.json"): # Dosya yoksa hata verme
        return {} # Boş bir sözlük döndür
    # 2. Dosyayı Aç: "r" (read) yani okuma modunda açıyoruz.
    with open("kullanicilar.json", "r", encoding="utf-8") as f:  #utf-8 türkçe karakter
    # 3. Dönüştür: JSON formatındaki metni Python sözlüğüne çevirir
        return json.load(f) # Dosyayı oku ve Python sözlüğüne çevir

def kullanici_ekle(isim, sifre):
    # 1. Önce Mevcut Bilgileri Al: 
    # Yukarıdaki 'verileri_oku' fonksiyonunu çağırıp eski kullanıcıları sepetimize alıyoruz.
    mevcut_veriler = verileri_oku() 

    # 2. Yeni Kullanıcıyı Sepete Ekle:
    # 'isim' anahtarı altına şifreyi ve ileride seçeceği haber tercihleri için boş bir liste ekliyoruz.
    mevcut_veriler[isim] = {"sifre": sifre, "tercihler": []} 
    
    # 3. Dosyaya Kalıcı Olarak Yaz:
    # "w" (write) yani yazma modunda dosyayı açıyoruz.
    with open("kullanicilar.json", "w", encoding="utf-8") as f:    #utf-8 türkçe karakter
        # 4. JSON'a Dönüştür: 
        # Python sözlüğünü tekrar JSON metnine çevirip dosyaya basıyoruz.
        # indent=4: Dosyanın insanlar tarafından da kolay okunmasını sağlar.
        json.dump(mevcut_veriler, f, ensure_ascii=False, indent=4)

def giris_kontrol(isim, sifre):
    veriler = verileri_oku()
    
    # Kullanıcı adı var mı diye bak
    if isim in veriler:
        # Şifreleri string (metin) olarak karşılaştır ve boşlukları temizle (.strip())
        kayitli_sifre = str(veriler[isim]["sifre"]).strip()
        girilen_sifre = str(sifre).strip()
        
        if kayitli_sifre == girilen_sifre:
            return True, veriler[isim]["tercihler"]
            
    return False, None
#-------------------------------------------------------------------------------------
