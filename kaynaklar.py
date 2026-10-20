"""RÂVÎ - Haber kaynakları (RSS havuzu).

HABER_ISTASYONU: {istasyon_adi: {kategori_adi: rss_url}}
ISTASYON_BILGI:  {istasyon_adi: (simge, kisa_aciklama)} - Ayarlar ekranında
                 kart başlığının yanında gösterilir.

Kaynakların RSS adresleri zaman zaman değişebilir; bir kaynak boş geliyorsa
o kategori sessizce atlanır (bkz. ravi.py _arka_plan), uygulama çökmez.
"""

OZEL_ON_EK = "Özel | "

# ============================================================== ANA AKIM
ntv_tam_liste = {
    "Son Dakika": "https://www.ntv.com.tr/gundem.rss",
    "Türkiye": "https://www.ntv.com.tr/turkiye.rss",
    "Dünya": "https://www.ntv.com.tr/dunya.rss",
    "Ekonomi": "https://www.ntv.com.tr/ekonomi.rss",
    "NTV Para": "https://www.ntv.com.tr/ntvpara.rss",
    "Teknoloji": "https://www.ntv.com.tr/teknoloji.rss",
    "Sağlık": "https://www.ntv.com.tr/saglik.rss",
    "Spor": "https://www.ntv.com.tr/spor.rss",
    "Otomobil": "https://www.ntv.com.tr/otomobil.rss",
    "Yaşam": "https://www.ntv.com.tr/yasam.rss",
    "Seyahat": "https://www.ntv.com.tr/seyahat.rss",
}

trt_haber_tam_liste = {
    "Manşetler": "https://www.trthaber.com/manset_articles.rss",
    "Son Dakika": "https://www.trthaber.com/sondakika_articles.rss",
    "Genel Son Dakika": "https://www.trthaber.com/sondakika.rss",
    "Gündem": "https://www.trthaber.com/gundem_articles.rss",
    "Dünya": "https://www.trthaber.com/dunya_articles.rss",
    "Ekonomi": "https://www.trthaber.com/ekonomi_articles.rss",
    "Bilim ve Teknoloji": "https://www.trthaber.com/bilim_teknoloji_articles.rss",
    "Spor": "https://www.trthaber.com/spor_articles.rss",
    "Sağlık": "https://www.trthaber.com/saglik_articles.rss",
    "Kültür-Sanat": "https://www.trthaber.com/kultur_sanat_articles.rss",
    "Yaşam": "https://www.trthaber.com/yasam_articles.rss",
}

cnn_turk_derin_arsiv = {
    "Günün Haberleri": "https://www.cnnturk.com/feed/rss/all/news",
    "Türkiye": "https://www.cnnturk.com/feed/rss/turkiye/news",
    "Dünya": "https://www.cnnturk.com/feed/rss/dunya/news",
    "Ekonomi": "https://www.cnnturk.com/feed/rss/ekonomi/news",
    "Teknoloji": "https://www.cnnturk.com/feed/rss/teknoloji/news",
    "Spor": "https://www.cnnturk.com/feed/rss/spor/news",
    "Sağlık": "https://www.cnnturk.com/feed/rss/saglik/news",
    "Kültür-Sanat": "https://www.cnnturk.com/feed/rss/kultur-sanat/news",
    "Otomobil": "https://www.cnnturk.com/feed/rss/otomobil/news",
    "Yaşam": "https://www.cnnturk.com/feed/rss/yasam/news",
}

bbc_derin_arsiv = {
    "Manşetler": "https://feeds.bbci.co.uk/turkce/rss.xml",
    "Türkiye": "https://feeds.bbci.co.uk/turkce/turkiye/rss.xml",
    "Bilim": "https://feeds.bbci.co.uk/turkce/bilim/rss.xml",
}

anadolu_ajansi_liste = {
    "Güncel": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "Politika": "https://www.aa.com.tr/tr/rss/default?cat=politika",
    "Ekonomi": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi",
    "Dünya": "https://www.aa.com.tr/tr/rss/default?cat=dunya",
    "Bilim-Teknoloji": "https://www.aa.com.tr/tr/rss/default?cat=bilim-teknoloji",
    "Spor": "https://www.aa.com.tr/tr/rss/default?cat=spor",
    "Sağlık": "https://www.aa.com.tr/tr/rss/default?cat=saglik",
    "Kültür": "https://www.aa.com.tr/tr/rss/default?cat=kultur",
    "Analiz": "https://www.aa.com.tr/tr/rss/default?cat=analiz",
}

haberturk_tam_liste = {
    "Tüm Haberler": "https://www.haberturk.com/rss",
    "Manşetler": "https://www.haberturk.com/rss/manset.xml",
    "Gündem": "https://www.haberturk.com/rss/gundem.xml",
    "Siyaset": "https://www.haberturk.com/rss/siyaset.xml",
    "Ekonomi": "https://www.haberturk.com/rss/ekonomi.xml",
    "Dünya": "https://www.haberturk.com/rss/dunya.xml",
    "Teknoloji": "https://www.haberturk.com/rss/teknoloji.xml",
    "Spor": "https://www.haberturk.com/rss/spor.xml",
    "Kültür-Sanat": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml",
    "Sinema": "https://www.haberturk.com/rss/kategori/sinema.xml",
    "Otomobil": "https://www.haberturk.com/rss/kategori/otomobil.xml",
    "Sağlık": "https://www.haberturk.com/rss/kategori/saglik.xml",
    "Yazarlar": "https://www.haberturk.com/rss/kategori/yazarlar.xml",
}

sozcu_tam_liste = {
    "Son Dakika": "https://www.sozcu.com.tr/feeds-son-dakika",
    "Tüm Haberler": "https://www.sozcu.com.tr/rss/tum-haberler.xml",
    "Gündem": "https://www.sozcu.com.tr/rss/gundem.xml",
    "Dünya": "https://www.sozcu.com.tr/rss/dunya.xml",
    "Ekonomi": "https://www.sozcu.com.tr/rss/ekonomi.xml",
    "Borsa": "https://www.sozcu.com.tr/feeds-rss-category-borsa",
    "Bilim ve Teknoloji": "https://www.sozcu.com.tr/rss/teknoloji.xml",
    "Spor": "https://www.sozcu.com.tr/rss/spor.xml",
    "Otomotiv": "https://www.sozcu.com.tr/rss/otomobil.xml",
    "Kültür-Sanat": "https://www.sozcu.com.tr/feeds-rss-category-kultur-sanat",
    "Sağlık": "https://www.sozcu.com.tr/rss/saglik.xml",
    "Yazarlar": "https://www.sozcu.com.tr/feeds-rss-category-yazar",
}

hurriyet_tam_liste = {
    "Anasayfa": "https://www.hurriyet.com.tr/rss/anasayfa",
    "Gündem": "https://www.hurriyet.com.tr/rss/gundem",
    "Siyaset": "https://www.hurriyet.com.tr/rss/siyaset",
    "Ekonomi": "https://www.hurriyet.com.tr/rss/ekonomi",
    "Dünya": "https://www.hurriyet.com.tr/rss/dunya",
    "Teknoloji": "https://www.hurriyet.com.tr/rss/teknoloji",
    "Spor": "https://www.hurriyet.com.tr/rss/spor",
    "Sağlık": "https://www.hurriyet.com.tr/rss/saglik",
    "Eğitim": "https://www.hurriyet.com.tr/rss/egitim",
    "Seyahat": "https://www.hurriyet.com.tr/rss/seyahat",
}

cumhuriyet_tam_liste = {
    "Tüm Haberler": "https://www.cumhuriyet.com.tr/rss",
    "Türkiye": "https://www.cumhuriyet.com.tr/rss/turkiye",
    "Siyaset": "https://www.cumhuriyet.com.tr/rss/siyaset",
    "Ekonomi": "https://www.cumhuriyet.com.tr/rss/ekonomi",
    "Dünya": "https://www.cumhuriyet.com.tr/rss/dunya",
    "Bilim-Teknoloji": "https://www.cumhuriyet.com.tr/rss/bilim-teknoloji",
    "Spor": "https://www.cumhuriyet.com.tr/rss/spor",
    "Sağlık": "https://www.cumhuriyet.com.tr/rss/saglik",
    "Yaşam": "https://www.cumhuriyet.com.tr/rss/yasam",
}

ulusal_basin_ozet = {
    "Milliyet Son Dakika": "https://www.milliyet.com.tr/rss/rssnew/sondakikarss.xml",
    "Milliyet Gündem": "https://www.milliyet.com.tr/rss/rssnew/gundemrss.xml",
    "Milliyet Ekonomi": "https://www.milliyet.com.tr/rss/rssnew/ekonomirss.xml",
    "Milliyet Teknoloji": "https://www.milliyet.com.tr/rss/rssnew/teknolojirss.xml",
    "Sabah Anasayfa": "https://www.sabah.com.tr/rss/anasayfa.xml",
    "Sabah Gündem": "https://www.sabah.com.tr/rss/gundem.xml",
    "Sabah Ekonomi": "https://www.sabah.com.tr/rss/ekonomi.xml",
    "Sabah Teknoloji": "https://www.sabah.com.tr/rss/teknoloji.xml",
    "Karar Gazetesi": "https://www.karar.com/service/rss.php",
    "Halk TV": "https://halktv.com.tr/service/rss.php",
    "Haber Global": "https://haberglobal.com.tr/rss",
    "Evrensel": "https://www.evrensel.net/rss/haber.xml",
    "En Son Haber": "https://www.ensonhaber.com/rss/ensonhaber.xml",
    "OdaTV": "https://www.odatv.com/rss.xml",
    "GZT": "https://www.gzt.com/rss",
}

# ================================================ BAĞIMSIZ & KÜRESEL
bagimsiz_ve_uluslararasi_medya = {
    "T24": "https://t24.com.tr/rss",
    "Diken": "https://www.diken.com.tr/feed/",
    "Gazete Duvar": "https://www.gazeteduvar.com.tr/export/rss",
    "Medyascope": "https://medyascope.tv/feed/",
    "Bianet": "https://bianet.org/rss/bianet",
    "Kısa Dalga": "https://kisadalga.net/service/rss.php",
    "Yetkin Report": "https://yetkinreport.com/feed/",
    "Serbestiyet": "https://serbestiyet.com/feed/",
    "Teyit.org": "https://teyit.org/feed?lang=tr",
    "Fayn": "https://www.fayn.press/rss/",
    "Journo": "https://journo.com.tr/feed",
    "İklim Haber": "https://www.iklimhaber.org/feed/",
    "Yeşil Gazete": "https://yesilgazete.org/feed/",
    "Euronews Türkçe": "https://tr.euronews.com/rss",
    "Independent Türkçe": "https://www.indyturk.com/rss.xml",
    "DW Türkçe": "http://rss.dw.com/rdf/rss-tur-all",
    "Sputnik Türkiye": "https://anlatilaninotesi.com.tr/export/rss2/archive/index.xml",
}

# ===================================================== TEKNOLOJİ
donanim_haber = {"Donanım Haber": "https://www.donanimhaber.com/rss/tum/"}
shiftdelete = {"ShiftDelete": "https://shiftdelete.net/feed"}
teknoloji_yeni_kaynaklar = {
    "Webtekno": "https://www.webtekno.com/rss.xml",
    "Technopat": "https://www.technopat.net/feed/",
    "Webrazzi Genel": "https://webrazzi.com/feed",
    "Webrazzi Yapay Zeka": "https://webrazzi.com/kategori/yapay-zeka/feed",
    "Webrazzi Yatırım": "https://webrazzi.com/kategori/yatirim/feed",
    "Teknoblog": "https://www.teknoblog.com/feed/",
    "LOG Dergisi": "https://www.log.com.tr/feed/",
    "CHIP Online": "https://www.chip.com.tr/rss/",
    "Sihirli Elma (Apple)": "https://www.sihirlielma.com/feed/",
    "Sordum.net": "https://www.sordum.net/feed/",
    "Donanım Günlüğü": "https://donanimgunlugu.com/feed",
    "Teknolojioku": "https://www.teknolojioku.com/export/rss",
}
teknoloji_birlesik = {**shiftdelete, **donanim_haber, **teknoloji_yeni_kaynaklar}

# ========================================================== BİLİM
bilim_istasyonu = {
    "Evrim Ağacı": "https://evrimagaci.org/rss.xml",
    "Arkeofili": "https://arkeofili.com/feed/",
    "Sarkaç (Bilim Akademisi)": "https://sarkac.org/feed/",
    "Herkese Bilim Teknoloji": "https://www.herkesebilimteknoloji.com/feed",
    "Kozmik Anafor": "https://www.kozmikanafor.com/feed/",
    "Matematiksel": "https://www.matematiksel.org/feed",
    "Bilimoloji": "https://www.bilimoloji.com/feed/",
}

# =============================================== EKONOMİ & KRİPTO
ekonomi_finans_kripto = {
    "Bloomberg HT": "https://www.bloomberght.com/rss/tum-haberler.xml",
    "Dünya Gazetesi": "https://www.dunya.com/rss?dunya",
    "Forbes Türkiye": "https://www.forbes.com.tr/rss",
    "Fortune Türkiye": "https://www.fortuneturkey.com/feed",
    "Capital": "https://www.capital.com.tr/rss/all",
    "Midas": "https://www.getmidas.com/feed/",
    "Bigpara": "https://bigpara.hurriyet.com.tr/rss/",
    "Döviz.com": "https://www.doviz.com/news/rss",
    "Investing Piyasa Özeti": "https://tr.investing.com/rss/market_overview.rss",
    "Investing Hisse": "https://tr.investing.com/rss/stock.rss",
    "CoinTürk (Kripto)": "https://www.coin-turk.com/feed",
    "BTCHaber (Kripto)": "https://www.btchaber.com/feed/",
}

# ==================================================== OYUN & SİNEMA
oyun_sinema_geek = {
    "Kayıp Rıhtım": "https://kayiprihtim.com/feed/",
    "Geekyapar": "https://geekyapar.com/feed/",
    "Bilimkurgu Kulübü": "https://www.bilimkurgukulubu.com/feed/",
    "IGN Türkiye": "https://tr.ign.com/feed.xml",
    "Oyungezer": "https://oyungezer.com.tr/rss",
    "Mobidictum": "https://mobidictum.com/tr/feed/",
    "Altyazı Sinema": "https://altyazi.net/feed/",
    "Beyazperde": "https://www.beyazperde.com/rss/haberler.xml",
    "Bigumigu": "https://bigumigu.com/feed/",
    "ListeList": "https://listelist.com/feed/",
}

# ===================================================== KÜLTÜR & DÜŞÜNCE
kultur_sanat_dusunce = {
    "Bant Mag": "https://bantmag.com/feed/",
    "Manifold": "https://manifold.press/rss",
    "Fikir Turu": "https://fikirturu.com/feed/",
    "Argonotlar": "https://argonotlar.com/feed/",
    "Arkitera (Mimarlık)": "https://www.arkitera.com/feed/",
    "5Harfliler": "https://www.5harfliler.com/feed/",
    "Edebiyat Haber": "https://www.edebiyathaber.net/feed/",
}

# ===================================================== OTOMOTİV & SPOR
otomotiv_ve_spor = {
    "Motor1 Türkiye (Tümü)": "https://tr.motor1.com/rss/articles/all/",
    "Motor1 Araç Testleri": "https://tr.motor1.com/rss/reviews/all/",
    "Motor1 Elektrikli/Hibrit": "https://tr.motor1.com/rss/category/electric-hybrid-vehicles/",
    "NTV Spor Anasayfa": "https://www.ntvspor.net/rss/anasayfa",
    "NTV Spor Futbol": "https://www.ntvspor.net/rss/kategori/futbol",
    "NTV Spor Basketbol": "https://www.ntvspor.net/rss/kategori/basketbol",
    "A Spor": "https://www.aspor.com.tr/rss/anasayfa.xml",
    "AjansSpor": "https://ajansspor.com/rss",
    "Fotomaç": "https://www.fotomac.com.tr/rss/anasayfa.xml",
    "Kontraspor": "https://kontraspor.com/rss",
}

# ============================================================= İSTASYON
HABER_ISTASYONU = {
    "NTV": ntv_tam_liste,
    "TRT Haber": trt_haber_tam_liste,
    "CNN Türk": cnn_turk_derin_arsiv,
    "BBC Türkçe": bbc_derin_arsiv,
    "Anadolu Ajansı": anadolu_ajansi_liste,
    "Habertürk": haberturk_tam_liste,
    "Sözcü": sozcu_tam_liste,
    "Hürriyet": hurriyet_tam_liste,
    "Cumhuriyet": cumhuriyet_tam_liste,
    "Ulusal Basın Özeti": ulusal_basin_ozet,
    "Bağımsız & Küresel": bagimsiz_ve_uluslararasi_medya,
    "Teknoloji": teknoloji_birlesik,
    "Bilim": bilim_istasyonu,
    "Ekonomi & Kripto": ekonomi_finans_kripto,
    "Oyun, Sinema & Geek": oyun_sinema_geek,
    "Kültür & Düşünce": kultur_sanat_dusunce,
    "Otomotiv & Spor": otomotiv_ve_spor,
}

# Ayarlar ekranında kart başlığının yanında gösterilen simge ve kısa tanım.
# Burada olmayan bir istasyon için ayarlar ekranı varsayılan bir simge kullanır.
ISTASYON_BILGI = {
    "NTV": ("📺", "Son dakika, ekonomi, teknoloji ve yaşam"),
    "TRT Haber": ("📡", "Kamu yayıncısından geniş kapsamlı haber akışı"),
    "CNN Türk": ("📰", "Gündem, ekonomi, spor ve kültür-sanat"),
    "BBC Türkçe": ("🌍", "Uluslararası bakış açısıyla Türkçe haber"),
    "Anadolu Ajansı": ("🏛️", "Resmi haber ajansından ham bültenler"),
    "Habertürk": ("📰", "Gündem, ekonomi ve yazarlar"),
    "Sözcü": ("📰", "Gündem, ekonomi ve köşe yazıları"),
    "Hürriyet": ("📰", "Geniş kapsamlı ana akım gazete"),
    "Cumhuriyet": ("📰", "Gündem, dünya ve kültür-sanat"),
    "Ulusal Basın Özeti": ("🗞️", "Milliyet, Sabah ve diğer gazetelerden seçmeler"),
    "Bağımsız & Küresel": ("🌐", "T24, Bianet, DW Türkçe ve benzeri bağımsız kaynaklar"),
    "Teknoloji": ("💻", "Webtekno, Technopat, Donanım Haber ve daha fazlası"),
    "Bilim": ("🔬", "Evrim Ağacı, Arkeofili ve popüler bilim siteleri"),
    "Ekonomi & Kripto": ("💰", "Piyasalar, döviz ve kripto para haberleri"),
    "Oyun, Sinema & Geek": ("🎮", "Oyun, sinema ve fantastik kurgu dünyası"),
    "Kültür & Düşünce": ("🎨", "Sanat, mimarlık, edebiyat ve fikir yazıları"),
    "Otomotiv & Spor": ("🚗", "Motor1, NTV Spor ve spor kulüpleri"),
}
