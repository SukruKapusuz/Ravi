"""RÂVÎ - Sabit haber kaynakları (RSS havuzu)."""

OZEL_ON_EK = "Özel | "

ntv_tam_liste = {
    "Son Dakika": "https://www.ntv.com.tr/gundem.rss",
    "Türkiye": "https://www.ntv.com.tr/turkiye.rss",
    "Dünya": "https://www.ntv.com.tr/dunya.rss",
    "Ekonomi": "https://www.ntv.com.tr/ekonomi.rss",
    "Teknoloji": "https://www.ntv.com.tr/teknoloji.rss",
    "Sağlık": "https://www.ntv.com.tr/saglik.rss",
    "Spor": "https://www.ntv.com.tr/spor.rss",
    "Otomobil": "https://www.ntv.com.tr/otomobil.rss",
}

trt_haber_tam_liste = {
    "Manşetler": "https://www.trthaber.com/manset_articles.rss",
    "Son Dakika": "https://www.trthaber.com/sondakika_articles.rss",
    "Gündem": "https://www.trthaber.com/gundem_articles.rss",
    "Ekonomi": "https://www.trthaber.com/ekonomi_articles.rss",
    "Spor": "https://www.trthaber.com/spor_articles.rss",
}

cnn_turk_derin_arsiv = {
    "Günün Haberleri": "https://www.cnnturk.com/feed/rss/all/news",
    "Dünya": "https://www.cnnturk.com/feed/rss/dunya/news",
    "Teknoloji": "https://www.cnnturk.com/feed/rss/teknoloji/news",
}

bbc_derin_arsiv = {
    "Manşetler": "https://feeds.bbci.co.uk/turkce/rss.xml",
    "Türkiye": "https://feeds.bbci.co.uk/turkce/turkiye/rss.xml",
    "Bilim": "https://feeds.bbci.co.uk/turkce/bilim/rss.xml",
}

donanim_haber = {"Donanım Haber": "https://www.donanimhaber.com/rss/tum/"}
shiftdelete = {"ShiftDelete": "https://shiftdelete.net/feed"}
teknoloji_birlesik = {**shiftdelete, **donanim_haber}

# Ana İstasyon: tüm kanallar tek çatı altında
HABER_ISTASYONU = {
    "NTV": ntv_tam_liste,
    "TRT": trt_haber_tam_liste,
    "CNN": cnn_turk_derin_arsiv,
    "BBC": bbc_derin_arsiv,
    "Teknoloji": teknoloji_birlesik,
}
