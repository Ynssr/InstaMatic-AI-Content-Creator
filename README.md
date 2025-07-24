# InstaMatic v3.1 - Yapay Zeka Destekli İçerik Üretim Stüdyosu

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python) ![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)

InstaMatic, statik görselleri Instagram için optimize edilmiş, dikkat çekici ve profesyonel gönderilere dönüştüren, Google Gemini Pro yapay zeka modeliyle güçlendirilmiş bir masaüstü uygulamasıdır.

<img width="1919" height="1028" alt="image" src="https://github.com/user-attachments/assets/cdc09037-1433-436f-914b-fb19caf5a7a8" />


---

## 🌟 Ana Özellikler

### Profesyonel Hizalama ve Kırpma Araçları
* **Esnek En-Boy Oranı:** Instagram'ın tüm popüler formatları (`4:5`, `1:1`, `9:16`, `1.91:1`) arasında tek tıkla geçiş yapma.
* **"Orijinal Oranı Koru":** Resminiz Instagram limitlerindeyse hiç kırpma yapmadan kullanma imkanı.
* **İnteraktif Kırpma:** Fare ile sürükleyerek mükemmel kompozisyonu yakalama.
* **Akıllı Kılavuzlar:**
    * **`Ctrl` Tuşu:** Kırpma kutusunu resmin tam merkezine bir mıknatıs gibi "yapıştırır" (Snap-to-guide).
    * **`Shift` Tuşu:** Sürükleme hareketini sadece dikey veya yatay eksene kilitleyerek hassas kaydırma sağlar (Axis-lock).

### Gelişmiş Tasarım ve Stil Kontrolü
* **Dinamik Metin Yerleşimi:** Metinleri resmin üstüne veya altına yerleştirme.
* **Tam Kontrol:** Font boyutu, metin genişliği (kenar boşlukları) ve arka plan yoğunluğu üzerinde hassas sayısal kontrol.
* **Özelleştirilebilir Renkler:** Renk paletinden metin ve yarı saydam arka plan için istenilen rengi seçme.
* **Metin Dış Çizgisi (Stroke):** Metin okunurluğunu artırmak için tek tıkla dış hat ekleme.
* **Otomatik Logo/Filigran:** Şirket veya kişisel logonuzu seçilen konuma ve yoğunluğa göre otomatik olarak ekleme.

### Yapay Zeka Yetenekleri (Google Gemini Pro)
* **Görsel Analiz (Image-to-Text):** Sadece resme bakarak sıfırdan, yaratıcı gönderi metinleri ve hashtag'ler üretme.
* **Stil Öğrenme:** `style_examples.txt` dosyasına eklenen örneklerden kullanıcının kendi yazım stilini öğrenme ve taklit etme.
* **Ton Seçimi:** "Haber Dili", "Samimi", "Profesyonel" gibi farklı tonlarda içerik üretme.
* **Korunacak Terimler:** Anime/Manga isimleri gibi özel terimlerin çevrilmesini veya değiştirilmesini engelleme.
* **Akıllı API Kullanımı:** Birden çok AI görevini (açıklama, çeviri, hashtag) tek bir istekte birleştirerek API limitlerini verimli kullanma.

### Kullanım Kolaylığı
* **Modern Koyu Tema:** Göz yormayan, şık ve kullanışlı arayüz.
* **Katlanabilir Menüler:** Dağınıklığı önleyen, odaklanmayı kolaylaştıran arayüz tasarımı.
* **Gelişmiş Font Tarayıcı:** Bilgisayarda yüklü fontları kendi stilleriyle önizleyerek seçme imkanı.
* **Ayar Hafızası:** Tüm stil, oran ve logo ayarlarının `config.json` dosyasına kaydedilip her açılışta geri yüklenmesi.

---

## 🛠️ Kurulum

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/SENIN_KULLANICI_ADIN/RepoAdin.git](https://github.com/SENIN_KULLANICI_ADIN/RepoAdin.git)
    cd RepoAdin
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    * Proje klasöründe `requirements.txt` adında bir dosya oluşturun ve içine aşağıdakileri yazın:
      ```
      Pillow
      google-generativeai
      fonttools
      ```
    * Ardından terminalde şu komutu çalıştırın:
      ```bash
      pip install -r requirements.txt
      ```

3.  **API Anahtarını Ayarlayın:**
    * Proje ana klasöründe `api_key.py` adında bir dosya oluşturun.
    * İçine `API_KEY = "BURAYA_KENDİ_API_ANAHTARINIZI_YAPIŞTIRIN"` satırını ekleyip kaydedin.

4.  **Programı Çalıştırın:**
    ```bash
    python instamatic.py
    ```
