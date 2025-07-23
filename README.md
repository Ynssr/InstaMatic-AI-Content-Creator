# InstaMatic - Yapay Zeka Destekli Instagram İçerik Asistanı

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python) ![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)

Bu proje, bir görseli ve metni alarak Instagram için optimize edilmiş, yapay zeka destekli, şık ve profesyonel gönderiler hazırlayan bir masaüstü uygulamasıdır.

<img width="1919" height="1026" alt="image" src="https://github.com/user-attachments/assets/016a04c7-b2cb-4db4-9555-3474dd246987" />


---

## 🌟 Ana Özellikler

# Gelişmiş Görsel Düzenleme
* İnteraktif Kırpma: 4:5 dikey formatta, fare ile sürükleyerek hassas kırpma.
* Profesyonel Hizalama: `Ctrl` tuşu ile merkeze yapışma (snap) ve `Shift` tuşu ile eksene kilitleme (axis-lock).
* Dinamik Metin Yerleşimi:
    * Yazı tipi, boyut, renk, konum (üst/alt) ve dış çizgi (stroke) ayarları.
    * Metin genişliği ve arka plan yoğunluğu üzerinde tam kontrol.
    * Manuel satır atlama (`Enter` tuşu) desteği.
* Otomatik Logo/Filigran: Seçilen bir logoyu resmin dört köşesinden birine otomatik olarak ekleme.

# Yapay Zeka Asistanı (Google Gemini Pro)
* Görsel Analiz: Sadece resme bakarak sıfırdan, yaratıcı gönderi metinleri ve hashtag'ler üretme.
* Stil Öğrenme: `style_examples.txt` dosyasına eklenen örneklerden kullanıcının yazım stilini öğrenme ve taklit etme.
* Ton Seçimi: "Haber Dili", "Samimi", "Profesyonel" gibi farklı tonlarda içerik üretme.
* Korunacak Terimler: Anime/Manga isimleri gibi özel terimlerin çevrilmesini engelleme.

# Kullanıcı Deneyimi
* Modern Koyu Tema: Göz yormayan, şık ve kullanışlı arayüz.
* Katlanabilir Menüler: Dağınıklığı önleyen, odaklanmayı kolaylaştıran arayüz tasarımı.
* Gelişmiş Font Tarayıcı: Bilgisayarda yüklü fontları kendi stilleriyle önizleyerek seçme imkanı.
* Ayar Hafızası: Tüm stil ve logo ayarlarının `config.json` dosyasına kaydedilip her açılışta geri yüklenmesi.

---

## 🛠️ Kurulum

1.  Projeyi Klonlayın:
    ```bash
    git clone [https://github.com/SENIN_KULLANICI_ADIN/RepoAdin.git](https://github.com/SENIN_KULLANICI_ADIN/RepoAdin.git)
    cd RepoAdin
    ```

2.  Gerekli Kütüphaneleri Yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
    *(Not: `requirements.txt` dosyasını oluşturmak için Adım 2'ye bakın)*

3.  API Anahtarını Ayarlayın:
    * Proje ana klasöründe `api_key.py` adında bir dosya oluşturun.
    * İçine `API_KEY = "BURAYA_KENDİ_API_ANAHTARINIZI_YAPIŞTIRIN"` satırını ekleyip kaydedin.

4.  Programı Çalıştırın:
    ```bash
    python instamatic.py
    ```

---

## 🚀 Kullanım

1.  Resim Seç: Üzerinde çalışmak istediğiniz görseli seçin.
2.  Kırp ve Hazırla: Kırmızı dörtgeni ayarladıktan sonra "Alanı Kırp ve Hazırla" butonuna basın.
3.  Stilleri Ayarla: Metin, renk, logo ve diğer tüm stil ayarlarını yapın. Değişiklikleri görmek için "Stil Değişikliklerini Uygula" butonuna basın.
4.  AI Asistanı: Metin kutularını doldurun ve AI Asistanı ile içeriklerinizi (açıklama, çeviri, hashtag) zenginleştirin.
5.  Kaydet: "Hazırlanan Resimleri Kaydet" butonu ile son çıktıları bilgisayarınıza indirin.
