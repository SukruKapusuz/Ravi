# RÂVÎ Haber Merkezi

Karmaşadan uzak, sade bir masaüstü RSS haber okuyucusu. Python ve Tkinter ile geliştirilmiştir.

## Özellikler
- **Tek Ekran:** NTV, TRT, BBC ve çeşitli teknoloji sitelerini tek ekrandan okuyun.
- **Akıcı Deneyim:** Haberler arka planda yüklenir, hızlı çalışır.
- **Kişiselleştirme:** Koyu mod, kendi RSS adresinizi ekleme ve "Beni hatırla" ile kalıcı oturum.

## Kullanım (Python Gerekmez)
Hiçbir kurulum yapmanıza gerek yok. GitHub'daki **Releases** veya **Actions** sekmesinden sisteminize uygun olanı indirin:
- **Windows:** İndirdiğiniz `RAVI.exe` dosyasına çift tıklayın.
- **Linux:** Arşivi çıkarın ve terminalde çalıştırın: 
  ```bash
  tar -xzf RAVI-linux.tar.gz && ./RAVI
  ```

## Geliştiriciler İçin
Kodu kendi bilgisayarınızda çalıştırmak için:
```bash
pip install -r requirements.txt
python ravi.py
```
*(Not: Kullanıcı ayarları Windows'ta `%APPDATA%\RAVI`, Linux'ta `~/.config/ravi` konumunda güvenle saklanır.)*

## Kendi Bilgisayarında Derleme
Uygulamayı tek bir dosyaya (exe/binary) dönüştürmek için:
```bash
pip install pyinstaller
pyinstaller --noconfirm ravi.spec
```
- **Önemli:** Windows sürümünü Windows'ta, Linux sürümünü Linux'ta derlemelisiniz. 
- *Linux kullanıcıları için:* Derlemeden önce sistemde `python3-tk` paketi kurulu olmalıdır (`sudo apt install python3-tk`).
