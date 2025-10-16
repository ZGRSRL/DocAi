# 🚀 SAP ME/MII Folder Analyzer — BURADAN BAŞLAYIN

## ✨ Hoş Geldiniz!

Bu proje, **SAP ME/MII** sistemlerindeki Java, XML ve konfigürasyon dosyalarını otomatik olarak analiz ederek mimari harita, entegrasyon noktaları ve eğitim materyalleri oluşturan bir **agent-based MVP** aracıdır.

---

## 📚 Dokümantasyon Rehberi

### 🎯 Hızlı Başlangıç (5 Dakika)
**Dosya:** [`QUICKSTART.md`](QUICKSTART.md)  
**Ne zaman okunmalı:** İlk kez kullanıyorsanız  
**İçerik:** Kurulum, test çalıştırma, temel kullanım

### 🔧 Kurulum Kılavuzu
**Dosya:** [`INSTALLATION.md`](INSTALLATION.md)  
**Ne zaman okunmalı:** Python kurulumu veya bağımlılık sorunları varsa  
**İçerik:** Python kurulumu, pip ayarları, sorun giderme

### 📖 Tam Dokümantasyon
**Dosya:** [`README.md`](README.md)  
**Ne zaman okunmalı:** Detaylı bilgi gerektiğinde  
**İçerik:** Tüm özellikler, parametreler, çıktı formatları

### 🏗️ Proje Genel Bakış
**Dosya:** [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)  
**Ne zaman okunmalı:** Mimari ve roadmap bilgisi için  
**İçerik:** Teknoloji stack, performans, gelecek özellikler

---

## ⚡ 3 Adımda Başlangıç

### 1️⃣ Bağımlılıkları Yükle

```powershell
pip install -r requirements.txt
```

### 2️⃣ Örnek Testi Çalıştır

**Seçenek A: PowerShell Script (Otomatik)**
```powershell
.\run_example.ps1
```

**Seçenek B: Manuel Komut**
```powershell
python me_mii_folder_analyzer.py --root ./example_test --out ./example_output
```

### 3️⃣ Çıktıları İncele

```powershell
type example_output\SUMMARY.md
```

---

## 📁 Proje Yapısı

```
DocAı/
│
├── 📄 00_START_HERE.md              ← Burdasınız (başlangıç noktası)
│
├── 📄 QUICKSTART.md                 ← 5 dakikalık hızlı başlangıç
├── 📄 INSTALLATION.md               ← Detaylı kurulum rehberi
├── 📄 README.md                     ← Tam dokümantasyon
├── 📄 PROJECT_OVERVIEW.md           ← Proje genel bakış
│
├── 🐍 me_mii_folder_analyzer.py     ← Ana script (600 satır)
├── 📋 requirements.txt              ← Python bağımlılıkları
├── 🔧 run_example.ps1               ← Otomatik test script'i
│
└── 📁 example_test/                 ← Test dosyaları
    ├── TestService.java             ← REST servis örneği
    ├── OrderTransaction.xml         ← MII Transaction
    ├── ProductService.wsdl          ← SOAP servis
    └── application.properties       ← Config dosyası
```

---

## 🎯 Ne Yapar?

### ✅ Analiz Edilen Dosyalar

| Dosya Tipi | Uzantı | Çıkarılan Bilgi |
|------------|--------|-----------------|
| **Java** | `.java` | REST endpoints (@Path, @GET), SQL/JDBC, HTTP calls |
| **XML** | `.xml` | MII BLS/Transaction steps, WSDL endpoints |
| **Config** | `.properties`, `.yaml`, `.yml`, `.json` | URLs, DSN strings |

### 📊 Üretilen Çıktılar

| Dosya | Açıklama | Kullanım |
|-------|----------|----------|
| **SUMMARY.md** | Mimari özet | Dokümantasyon, sunumlar |
| **TRAINING.md** | Eğitim materyali | Onboarding, rol tanımları |
| **graph.mmd** | Mermaid diyagram | Görsel ilişki haritası |
| **graph.json** | JSON ilişkiler | Programatik analiz, Neo4j import |

---

## 🚦 Kullanım Senaryoları

### 📌 Senaryo 1: Yeni Ekip Üyesi Onboarding
```powershell
# Projeyi analiz et
python me_mii_folder_analyzer.py --root "D:/SAP_ME_Project" --out ./onboarding

# TRAINING.md ve SUMMARY.md'yi yeni üyeyle paylaş
```

### 📌 Senaryo 2: REST Endpoint Envanteri
```powershell
# Tüm endpoint'leri tespit et
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./endpoints

# SUMMARY.md içinde "REST/SOAP & Diğer Uç Noktalar" bölümüne bak
```

### 📌 Senaryo 3: Veritabanı Bağımlılık Analizi
```powershell
# DB erişimlerini tespit et
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./db_analysis

# SUMMARY.md içinde "Olası Veritabanı Erişimleri" bölümüne bak
```

### 📌 Senaryo 4: Dış Sistem Entegrasyonları
```powershell
# Entegrasyon noktalarını bul
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./integrations

# graph.json içinde "SERVICE_CALLS_HTTP" ve "SOAP_DEF" ara
```

---

## 🛠️ Teknoloji

### Python Bağımlılıkları
- **javalang** — Java AST parsing
- **lxml** — XML/XPath parsing
- **networkx** — Graf yapısı
- **pydantic** — Veri validasyon
- **click** — CLI interface
- **rich** — Terminal formatting

### Minimum Gereksinimler
- Python 3.8+
- 100 MB RAM
- Windows/Linux/macOS

---

## 📖 Örnek Kullanım

### Temel Komut
```powershell
python me_mii_folder_analyzer.py --root "D:/MyProject" --out ./analysis
```

### Parametreler
```powershell
--root      # Analiz edilecek klasör (zorunlu)
--out       # Çıktı klasörü (varsayılan: ./out)
--mermaid   # Mermaid grafik oluştur (varsayılan: True)
--jsonedges # JSON kenar dosyası oluştur (varsayılan: True)
```

### Yardım
```powershell
python me_mii_folder_analyzer.py --help
```

---

## 🎓 Öğrenme Yolu

### Seviye 1: Başlangıç (15 dakika)
1. ✅ Bu dosyayı okuyun (`00_START_HERE.md`)
2. ✅ `QUICKSTART.md` ile test edin
3. ✅ `example_output/` çıktılarını inceleyin

### Seviye 2: Kullanım (30 dakika)
1. ✅ `README.md` tam dokümantasyonu okuyun
2. ✅ Kendi projenizle deneyin
3. ✅ Çıktıları ekibinizle paylaşın

### Seviye 3: İleri Seviye (1 saat)
1. ✅ `PROJECT_OVERVIEW.md` mimariyi anlayın
2. ✅ `me_mii_folder_analyzer.py` kaynak kodunu inceleyin
3. ✅ TODO bölümünde gelecek özellikleri görün

---

## 🆘 Sorun mu Yaşıyorsunuz?

### ❌ Python bulunamadı
**Çözüm:** [`INSTALLATION.md`](INSTALLATION.md) → "Python Kurulumu" bölümü

### ❌ Bağımlılık hatası
**Çözüm:**
```powershell
pip install -r requirements.txt
```

### ❌ Analiz çok yavaş
**Çözüm:** Alt klasör bazlı analiz yapın
```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME/services" --out ./services
python me_mii_folder_analyzer.py --root "D:/SAP_ME/transactions" --out ./transactions
```

### ❌ Dosyalar tespit edilmiyor
**Çözüm:** MVP heuristik kullanır. Gelecek versiyonlarda geliştirilecek.

---

## 🚀 Hızlı Test

### Otomatik Test (Önerilen)
```powershell
.\run_example.ps1
```

Bu script:
1. ✅ Python kurulumunu kontrol eder
2. ✅ Bağımlılıkları yükler (gerekirse)
3. ✅ Örnek analizi çalıştırır
4. ✅ Sonuçları gösterir

### Manuel Test
```powershell
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Analizi çalıştır
python me_mii_folder_analyzer.py --root ./example_test --out ./example_output

# 3. Sonuçları görüntüle
type example_output\SUMMARY.md
```

---

## 🎯 Sonraki Adımlar

### ✅ Tamamladıysanız:
- [x] Örnek test çalıştırıldı
- [x] Çıktılar incelendi
- [x] Dokümantasyon okundu

### 🎯 Şimdi Yapabilirsiniz:
1. **Kendi projenizi analiz edin:**
   ```powershell
   python me_mii_folder_analyzer.py --root "D:/YourProject" --out ./your_analysis
   ```

2. **Çıktıları ekibinizle paylaşın:**
   - `SUMMARY.md` → Teknik sunumlar
   - `TRAINING.md` → Yeni üye onboarding
   - `graph.mmd` → Mermaid viewer'da görselleştirin

3. **İleri seviye özellikler için:**
   - `PROJECT_OVERVIEW.md` → Roadmap
   - Script içi TODO → Gelecek geliştirmeler

---

## 📞 Destek

### Dokümantasyon
- [`QUICKSTART.md`](QUICKSTART.md) — Hızlı başlangıç
- [`INSTALLATION.md`](INSTALLATION.md) — Kurulum sorunları
- [`README.md`](README.md) — Detaylı kullanım
- [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) — Mimari ve roadmap

### Topluluk
- Script içi TODO bölümü — Bilinen kısıtlamalar
- Teknik destek ekibi — Çözülemeyen sorunlar

---

## 🎉 Başarılar!

Artık SAP ME/MII projelerinizi analiz etmeye hazırsınız!

```powershell
# Hemen başlayın:
python me_mii_folder_analyzer.py --root "D:/YourProject" --out ./analysis
```

**İyi analizler! 🚀**

---

**Proje Durumu:** ✅ MVP Tamamlandı  
**Versiyon:** 1.0.0  
**Son Güncelleme:** 2025-01
