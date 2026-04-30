# RAVI Haber Merkezi

Bu çalışma, Python dili ve Tkinter arayüz kütüphanesi kullanılarak geliştirilmiş bir RSS haber okuma uygulamasıdır. Projenin temel amacı, farklı haber kaynaklarından alınan verileri tek bir merkezde toplayarak kullanıcıya kişiselleştirilmiş bir okuma deneyimi sunmaktır.

## Projenin Özellikleri
- Kullanıcı yetkilendirme (kayıt ve giriş) sistemi.
- Kullanıcı tercihlerinin ve bilgilerinin JSON formatında yerel olarak depolanması.
- RSS (Rich Site Summary) teknolojisi ile anlık haber çekimi.
- Kategori bazlı haber filtreleme (Gündem, Teknoloji, Ekonomi vb.).
- Haber detaylarını görüntüleme ve kaynak siteye yönlendirme.

## Gereksinimler
Uygulamanın çalışabilmesi için sistemde Python yüklü olmalı ve haber akışlarını işleyebilmek için gerekli olan feedparser kütüphanesi kurulmalıdır:

pip install feedparser

## Çalıştırma Talimatı
Proje birbiriyle etkileşimli modüllerden oluşmaktadır. Uygulamanın veri tutarlılığını sağlaması ve oturum yönetimini doğru yapabilmesi için mutlaka ana giriş dosyasından başlatılması gerekir.

Başlatma komutu:
python hesap_aç.py

Uygulama çalıştırıldığında kullanıcıyı önce giriş ekranı karşılar. Kimlik doğrulaması yapıldıktan sonra haber seçim paneline geçiş yapılır.

## Dosya İçerikleri ve Yapısı
- hesap_aç.py: Uygulamanın başlangıç dosyasıdır. Giriş ve kayıt fonksiyonlarını içerir.
- ana_dosya.py: Haber kaynaklarının yönetimini ve kategori seçimlerini sağlar.
- Haber_paneli.py: Haberlerin listelendiği ve içeriklerin okunduğu arayüzdür.
- giriş/: Uygulama arayüzünde kullanılan görselleri barındıran dizindir.
