# RAVI Haber Merkezi

Python ve Tkinter ile yazılmış RSS haber okuyucu. Birden fazla haber kaynağını tek ekranda toplar.

## Özellikler

- Kayıt ve giriş sistemi; "Beni hatırla" ile oturum açık kalır, uygulama açılınca doğrudan haber ekranı gelir.
- Haber ekranından Ayarlar: Haber kaynaklarını değiştirme, özel RSS ekleme, koyu mod, çıkış yapma.
- Kategori bazlı haber seçimi (NTV, TRT, CNN Türk, BBC Türkçe, teknoloji siteleri).
- Haberler arka planda yüklenir, pencere donmaz.
- Windows ve Linux için Python kurmadan çalışan tek dosyalık sürüm.

## Kullanıcılar için (Python gerekmez)

GitHub'daki **Actions** sekmesinden son derlemeyi ya da **Releases** bölümünü açın:

- **Windows:** `RAVI.exe` dosyasına çift tıklayın.
- **Linux:**
  ```bash
  tar -xzf RAVI-linux.tar.gz && ./RAVI
  ```

## Geliştiriciler için

```bash
pip install -r requirements.txt
python ravi.py
```

Veriler (kullanıcılar, oturum, tema) çalışma klasörüne değil kullanıcı veri klasörüne yazılır: Windows'ta `%APPDATA%\RAVI`, Linux'ta `~/.config/ravi`.

## Kendi bilgisayarında derleme

```bash
pip install pyinstaller
pyinstaller --noconfirm ravi.spec
```

PyInstaller çapraz derleme yapmaz: Windows sürümü Windows'ta, Linux sürümü Linux'ta derlenir (Linux'ta önce `sudo apt install python3-tk` kurulmalıdır). İkisini de otomatik üretmek için `.github/workflows/derle.yml` kullanılır.

Pencere simgesi için `ravi_logo.ico` (Windows) ve `ravi_logo.png` (Linux) dosyalarını `ravi.py`'nin yanına koyun.

## Dosyalar

| Dosya | Görevi |
| :--- | :--- |
| `ravi.py` | Uygulama: giriş, haber ve ayar ekranları |
| `depo.py` | Kullanıcılar, kalıcı oturum, ayarların saklanması |
| `kaynaklar.py` | Sabit RSS kaynak listesi |
| `ravi.spec` | PyInstaller derleme tarifi |
