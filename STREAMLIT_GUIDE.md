# 🎨 Streamlit Web UI Kullanım Kılavuzu

## 🚀 Başlatma

### Komut Satırından
```powershell
streamlit run streamlit_app.py
```

veya Python ile:
```powershell
python -m streamlit run streamlit_app.py
```

### Otomatik Tarayıcı Açılması
Streamlit otomatik olarak varsayılan tarayıcınızda açılacaktır:
- **URL:** http://localhost:8501

---

## 📁 Klasör Seçimi — İki Yöntem

### Yöntem 1: Manuel Yol Girişi
1. Sol menüde **"Manuel Yol Gir"** seçeneğini seçin
2. Klasör yolunu yazın (örn: `D:/SAP_ME_Project`)
3. Enter'a basın

### Yöntem 2: Klasör Tarayıcı ⭐ (Önerilen)
1. Sol menüde **"Klasör Tarayıcı"** seçeneğini seçin
2. **Mevcut Konum** kutusunda şu anki konumunuzu görürsünüz
3. **Alt Klasörler** listesinden istediğiniz klasörü bulun
4. Klasörün yanındaki **✓** butonuna tıklayarak o klasöre girin
5. **⬆️ Üst Klasör** butonu ile bir üst dizine çıkabilirsiniz
6. **🔄** butonu ile listeyi yenileyebilirsiniz
7. İstediğiniz klasöre ulaştığınızda **✅ Bu Klasörü Kullan** butonuna tıklayın

#### Klasör Tarayıcı Özellikleri
- 📁 Sadece klasörler gösterilir (dosyalar gizlidir)
- 🔢 İlk 20 klasör gösterilir (performans için)
- ⚡ Hızlı navigasyon
- 🔒 İzin hatalarını gösterir

---

## ⚙️ Analiz Ayarları

### Çıktı Klasörü
- Varsayılan: `./streamlit_output`
- Analiz sonuçlarının kaydedileceği yer
- Otomatik oluşturulur (yoksa)

### Çıktı Formatları
- ✅ **Mermaid Diyagram (.mmd)** — Görsel ilişki haritası
- ✅ **JSON İlişkiler (.json)** — Programatik erişim için

---

## 🎯 Analiz Çalıştırma

1. **Klasör seçin** (yukarıdaki yöntemlerden biri ile)
2. **Çıktı klasörünü** belirleyin
3. **Çıktı formatlarını** seçin
4. **🚀 Analizi Başlat** butonuna tıklayın
5. **Progress bar** ile ilerlemeyi takip edin

### Analiz Aşamaları
```
🔍 Analiz başlatılıyor...     (10%)
⚙️ Dosyalar taranıyor...      (30%)
📊 Sonuçlar işleniyor...      (70%)
✅ Analiz tamamlandı!         (100%)
```

---

## 📊 Sonuçları İnceleme

Analiz tamamlandığında **5 sekme** görünür:

### 1️⃣ Özet Rapor
- **İçerik:** SUMMARY.md dosyası
- **Bilgiler:**
  - Java sınıf sayısı
  - BLS/Transaction adımları
  - İlişki sayısı
  - Endpoint'ler
  - DB erişimleri
- **Kullanım:** Hızlı genel bakış

### 2️⃣ Eğitim Dökümanı
- **İçerik:** TRAINING.md dosyası
- **Bilgiler:**
  - Rol tanımları (Operatör, Süpervizör, Admin)
  - İş akışı örnekleri
  - SSS iskeleti
  - Sorun giderme
- **Kullanım:** Yeni ekip üyesi onboarding

### 3️⃣ Mermaid Diyagram
- **İçerik:** graph.mmd dosyası
- **Özellikler:**
  - Kod görünümü
  - Kopyalama kolaylığı
  - Mermaid Live Editor linki
- **Görselleştirme:** 
  - Kodu kopyalayın
  - https://mermaid.live adresine gidin
  - Yapıştırın ve diyagramı görün

### 4️⃣ JSON Veriler
- **İçerik:** graph.json dosyası
- **Görünümler:**
  - JSON ağacı (interaktif)
  - Tablo görünümü (Pandas DataFrame)
  - İlişki tipi dağılımı (bar chart)
- **Kullanım:** Programatik analiz, Neo4j import

### 5️⃣ İndir
- **Tek tek indirme:**
  - 📄 SUMMARY.md
  - 📚 TRAINING.md
  - 🎨 graph.mmd
  - 📊 graph.json
- **Toplu indirme:**
  - 📦 Tüm dosyaları ZIP olarak indir

---

## 📈 Metrikler (Dashboard)

Analiz sonrası üstte **5 metrik kartı** görünür:

| Metrik | Açıklama |
|--------|----------|
| **Java Sınıfları** | Tespit edilen Java class sayısı |
| **BLS Adımları** | MII BLS/Transaction step sayısı |
| **İlişkiler** | Toplam ilişki kenarı sayısı |
| **Endpoint'ler** | REST/SOAP/Config URL sayısı |
| **DB Erişimleri** | Veritabanı bağlantı sayısı |

---

## 🎨 Kullanıcı Arayüzü Özellikleri

### Ana Sayfa (Analiz Öncesi)
- ✨ **Özellikler** bölümü (3 sütun)
- 🚀 **Hızlı Başlangıç** rehberi
- 📖 **Örnek Kullanım** (genişletilebilir)
- ⚙️ **Sistem Gereksinimleri** (genişletilebilir)

### Sidebar (Sol Menü)
- 🖼️ Logo/Banner
- ⚙️ Ayarlar bölümü
- 📁 Klasör seçimi
- 📊 Çıktı formatları
- 🚀 Analiz butonu
- 📚 Hızlı bağlantılar

### Renkli Kutular
- 🟢 **Yeşil:** Başarı mesajları
- 🔵 **Mavi:** Bilgi mesajları
- 🟡 **Sarı:** Uyarılar
- 🔴 **Kırmızı:** Hatalar

---

## 🔍 Örnek Kullanım Senaryosu

### Senaryo: Yeni Proje Analizi

1. **Streamlit'i başlat:**
   ```powershell
   streamlit run streamlit_app.py
   ```

2. **Tarayıcıda açılan sayfada:**
   - Sol menüden "Klasör Tarayıcı" seç
   - D: sürücüsüne git
   - SAP_ME_Project klasörünü bul
   - ✓ butonuna tıklayarak klasöre gir
   - Alt klasörleri gez
   - "src" veya "main" klasörüne ulaş
   - "✅ Bu Klasörü Kullan" butonuna tıkla

3. **Çıktı ayarları:**
   - Çıktı klasörü: `./my_analysis`
   - Mermaid: ✅ Aktif
   - JSON: ✅ Aktif

4. **Analizi başlat:**
   - "🚀 Analizi Başlat" butonuna tıkla
   - Progress bar'ı izle
   - Tamamlanmasını bekle

5. **Sonuçları incele:**
   - Metriklere bak (üstte)
   - "Özet Rapor" sekmesini oku
   - "Mermaid Diyagram" sekmesinden kodu kopyala
   - Mermaid Live'da görselleştir
   - "JSON Veriler" sekmesinde tabloyu incele
   - "İndir" sekmesinden ZIP indir

---

## 💡 İpuçları

### Performans
- ✅ Küçük klasörlerle test edin (örn: `./example_test`)
- ✅ Büyük projelerde alt klasör bazlı analiz yapın
- ✅ Gereksiz formatları kapatın (hız için)

### Klasör Seçimi
- 📁 Klasör tarayıcıda sadece klasörler görünür
- ⬆️ Üst klasör butonu ile hızlı navigasyon
- 🔄 Yenile butonu ile listeyi güncelleyin
- 💾 "Bu Klasörü Kullan" ile seçimi onaylayın

### Sonuçlar
- 📊 JSON tablosunu Excel'e export edebilirsiniz
- 🎨 Mermaid diyagramını PNG olarak kaydedebilirsiniz
- 📦 ZIP indirme ile tüm dosyaları tek seferde alın
- 🔗 Mermaid Live Editor'de diyagramı düzenleyebilirsiniz

### Hata Durumunda
- ❌ Klasör bulunamadı → Yolu kontrol edin
- ❌ İzin hatası → Yönetici olarak çalıştırın
- ❌ Python bulunamadı → PATH'e ekleyin
- ❌ Bağımlılık hatası → `pip install -r requirements.txt`

---

## 🎯 Klavye Kısayolları

Streamlit varsayılan kısayolları:
- **R** — Uygulamayı yeniden çalıştır
- **C** — Önbelleği temizle
- **Ctrl+C** (Terminal) — Uygulamayı durdur

---

## 🌐 Tarayıcı Desteği

### Desteklenen Tarayıcılar
- ✅ Google Chrome (önerilen)
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Safari

### Önerilen Çözünürlük
- Minimum: 1280x720
- Önerilen: 1920x1080

---

## 🔧 Gelişmiş Ayarlar

### Port Değiştirme
```powershell
streamlit run streamlit_app.py --server.port 8502
```

### Headless Mod (Tarayıcı Açmadan)
```powershell
streamlit run streamlit_app.py --server.headless true
```

### Tema Değiştirme
Sağ üst köşedeki ⚙️ Settings → Theme → Light/Dark

---

## 📱 Mobil Uyumluluk

Streamlit responsive tasarıma sahiptir:
- 📱 Mobil cihazlarda kullanılabilir
- 💻 Tablet'te optimize görünüm
- 🖥️ Desktop'ta tam özellik

---

## 🆘 Sorun Giderme

### Streamlit Başlamıyor
```powershell
# Streamlit kurulu mu kontrol et
pip list | findstr streamlit

# Yoksa kur
pip install streamlit

# Versiyonu kontrol et
streamlit --version
```

### Port Zaten Kullanımda
```powershell
# Farklı port kullan
streamlit run streamlit_app.py --server.port 8502
```

### Klasör Tarayıcı Çalışmıyor
- Windows'ta yönetici olarak çalıştırın
- Klasör izinlerini kontrol edin
- Manuel yol girişi kullanın

---

## 🎉 Başarı Hikayeleri

### Örnek 1: Hızlı Dokümantasyon
**Durum:** 500 dosyalık proje, dokümantasyon yok  
**Çözüm:** 
1. Streamlit'te klasörü seç
2. Analizi çalıştır (2 dakika)
3. SUMMARY.md'yi indir
4. Ekiple paylaş

**Sonuç:** 2 haftalık iş → 2 dakika

### Örnek 2: Görsel Sunum
**Durum:** Yöneticiye mimari sunumu yapılacak  
**Çözüm:**
1. Analiz çalıştır
2. Mermaid diyagramını kopyala
3. Mermaid Live'da PNG olarak kaydet
4. PowerPoint'e ekle

**Sonuç:** Profesyonel görsel hazır

---

## 📚 Ek Kaynaklar

- [Streamlit Dokümantasyonu](https://docs.streamlit.io)
- [Mermaid Syntax](https://mermaid.js.org/syntax/flowchart.html)
- [Pandas Cheat Sheet](https://pandas.pydata.org/docs/)

---

**🎨 Streamlit UI ile SAP ME/MII analizleriniz artık çok daha kolay!**

**Versiyon:** 1.0.0  
**Son Güncelleme:** 2025-01
