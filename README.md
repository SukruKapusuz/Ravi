# RAVI Haber Merkezi

Python ve Tkinter ile yazılmış RSS haber okuyucu. Birden fazla haber kaynağını tek ekranda toplar.

## Özellikler

- Kayıt / giriş sistemi; **"Beni hatırla"** ile oturum açık kalır, uygulama açılınca doğrudan haber ekranı gelir
- Haber ekranından **Ayarlar**: haber kaynaklarını değiştirme, özel RSS ekleme, **koyu mod**, **çıkış yap**
- Kategori bazlı haber seçimi (NTV, TRT, CNN Türk, BBC Türkçe, teknoloji siteleri)
- **Kişiselleştirme:** tıkladığınız haberlerden ilgi alanınızı öğrenir ve akışı ona göre sıralar; okunanlar soluk renkte alta iner, "✕ Gizle" ile istemediğiniz haberi kaldırırsınız. Listenin %20'si, ilgi göstermediğiniz kaynaklardan "keşif" haberleridir (tek kaynağa sıkışmayın diye)
- Haberler arka planda yüklenir, pencere donmaz
- Windows ve Linux için Python kurmadan çalışan tek dosyalık sürüm

## Kullanıcılar için (Python gerekmez)

GitHub'daki **Actions** sekmesinden son derlemeyi ya da **Releases** bölümünü açın:

- **Windows:** `RAVI.exe` dosyasına çift tıklayın.
- **Linux:** `tar -xzf RAVI-linux.tar.gz && ./RAVI`

## Geliştiriciler için

```
pip install -r requirements.txt
python ravi.py
```

Veriler (kullanıcılar, oturum, tema, öğrenilen ilgi alanları) çalışma klasörüne değil kullanıcı veri klasörüne yazılır:
Windows `%APPDATA%\RAVI`, Linux `~/.config/ravi`.

### Gizlilik

Hiçbir veri internete gönderilmez. Okuma alışkanlıkları şifre dosyasından ayrı, `profil.json` içinde tutulur.
**Ayarlar → Kişiselleştirme** bölümünden öğrenme kapatılabilir (kapalıyken hiçbir şey kaydedilmez ve sıralamada kullanılmaz) ya da öğrenilenler tamamen silinebilir.

### Kendi bilgisayarında derleme

```
pip install pyinstaller
pyinstaller --noconfirm ravi.spec
```

PyInstaller çapraz derleme yapmaz: Windows sürümü Windows'ta, Linux sürümü Linux'ta derlenir
(Linux'ta önce `sudo apt install python3-tk`). İkisini de otomatik üretmek için
`.github/workflows/derle.yml` kullanılır.

Pencere simgesi için `ravi_logo.ico` (Windows) ve `ravi_logo.png` (Linux) dosyalarını `ravi.py`'nin yanına koyun.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `ravi.py` | Uygulama: giriş, haber ve ayar ekranları |
| `depo.py` | Kullanıcılar, kalıcı oturum, ayarlar ve öğrenilen profilin saklanması |
| `mizan.py` | Kişiselleştirme motoru: puanlama, öğrenme, soğuma, sıralama (arayüzden bağımsız) |
| `kaynaklar.py` | Sabit RSS kaynak listesi |
| `ravi.spec` | PyInstaller derleme tarifi |
