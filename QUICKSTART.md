# 🚀 Quick Start Guide — SAP ME/MII Folder Analyzer

## 5 Dakikada Başlangıç

### 1️⃣ Python Kurulumunu Kontrol Et

```powershell
python --version
```

Eğer Python kurulu değilse → [INSTALLATION.md](INSTALLATION.md) dosyasına bakın.

### 2️⃣ Bağımlılıkları Yükle

```powershell
pip install -r requirements.txt
```

### 3️⃣ Test Verisiyle Dene

Proje içinde örnek test klasörü hazır:

```powershell
python me_mii_folder_analyzer.py --root ./example_test --out ./test_output
```

### 4️⃣ Çıktıları İncele

```powershell
# Özet raporu
type test_output\SUMMARY.md

# Eğitim dökümanı
type test_output\TRAINING.md

# Mermaid grafik
type test_output\graph.mmd

# JSON ilişkiler
type test_output\graph.json
```

### 5️⃣ Kendi Projenle Çalıştır

```powershell
python me_mii_folder_analyzer.py --root "D:/YourSAPProject" --out ./analysis_output
```

---

## 📊 Ne Tespit Eder?

### ✅ Java Dosyalarından:
- REST endpoint'ler (`@Path`, `@GET`, `@POST`, vb.)
- SQL sorguları ve JDBC bağlantıları
- Dış HTTP çağrıları

### ✅ XML Dosyalarından:
- MII BLS/Transaction adımları
- WSDL SOAP servisleri
- Endpoint location'ları

### ✅ Config Dosyalarından:
- URL'ler (http://, https://)
- JDBC DSN string'leri

---

## 📁 Örnek Çıktı Yapısı

```
test_output/
├── SUMMARY.md          # Mimari özet
├── TRAINING.md         # Eğitim dökümanı
├── graph.mmd           # Mermaid diyagram
└── graph.json          # İlişki verileri
```

---

## 🎯 Örnek Kullanım Senaryoları

### Senaryo 1: Tüm REST Endpoint'leri Bul

```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./endpoints_analysis
# SUMMARY.md içinde "REST/SOAP & Diğer Uç Noktalar" bölümüne bak
```

### Senaryo 2: Veritabanı Bağımlılıklarını Tespit Et

```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./db_analysis
# SUMMARY.md içinde "Olası Veritabanı Erişimleri" bölümüne bak
```

### Senaryo 3: Dış Sistem Entegrasyonlarını Listele

```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./integration_analysis
# graph.json içinde "SERVICE_CALLS_HTTP" ve "SOAP_DEF" tipli kenarları ara
```

### Senaryo 4: MII Transaction Akışlarını Görselleştir

```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME" --out ./flow_analysis
# graph.mmd dosyasını Mermaid viewer'da aç (örn: https://mermaid.live)
```

---

## 🔍 Çıktıları Nasıl Kullanırım?

### SUMMARY.md
- **Amaç:** Hızlı mimari genel bakış
- **Kullanım:** Proje dokümantasyonu, teknik sunumlar
- **İçerik:** İstatistikler, endpoint listesi, DB erişimleri

### TRAINING.md
- **Amaç:** Yeni ekip üyelerinin onboarding'i
- **Kullanım:** Eğitim materyali, rol tanımları
- **İçerik:** Operatör/Süpervizör/Admin görevleri, SSS

### graph.mmd
- **Amaç:** Görsel ilişki haritası
- **Kullanım:** Mermaid viewer'da açın (VS Code, mermaid.live)
- **İçerik:** Servis → Endpoint → DB ilişkileri

### graph.json
- **Amaç:** Programatik analiz
- **Kullanım:** Python/JavaScript ile işleyin, Neo4j'ye import edin
- **İçerik:** Tüm ilişkiler JSON array formatında

---

## 💡 İpuçları

### 🎨 Mermaid Grafiğini Görselleştir

1. https://mermaid.live adresine git
2. `graph.mmd` içeriğini kopyala-yapıştır
3. Otomatik diyagram oluşur

### 📊 JSON'u Excel'e Aktar

```powershell
# Python ile CSV'ye çevir
python -c "import json, csv; data=json.load(open('test_output/graph.json')); csv.writer(open('edges.csv','w',newline='')).writerows([data[0].keys()]+[[d[k] for k in d] for d in data])"
```

### 🔎 Belirli Bir Servisi Ara

```powershell
# SUMMARY.md içinde ara
findstr /i "OrderService" test_output\SUMMARY.md

# graph.json içinde ara
findstr /i "OrderService" test_output\graph.json
```

---

## ❓ Sık Sorulan Sorular

**S: Python kurulu değil, ne yapmalıyım?**  
C: [INSTALLATION.md](INSTALLATION.md) dosyasındaki adımları takip edin.

**S: Analiz çok uzun sürüyor?**  
C: Büyük projelerde alt klasör bazlı analiz yapın. Örnek:
```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME/services" --out ./services_analysis
python me_mii_folder_analyzer.py --root "D:/SAP_ME/transactions" --out ./transactions_analysis
```

**S: Bazı dosyalar tespit edilmiyor?**  
C: MVP heuristik kullanır. Gelecek versiyonlarda daha gelişmiş parsing eklenecek.

**S: Çıktıları nasıl paylaşırım?**  
C: `out/` klasörünü ZIP'leyip paylaşın veya Git'e commit edin.

**S: Neo4j'ye nasıl import ederim?**  
C: `graph.json` dosyasını Cypher script'e çevirin:
```cypher
// Örnek Cypher
UNWIND $edges AS edge
MERGE (a:Node {name: edge.src})
MERGE (b:Node {name: edge.dst})
MERGE (a)-[r:RELATION {type: edge.type}]->(b)
```

---

## 🆘 Sorun mu Yaşıyorsun?

1. ✅ [INSTALLATION.md](INSTALLATION.md) — Kurulum sorunları
2. ✅ [README.md](README.md) — Detaylı dokümantasyon
3. ✅ Script içindeki TODO bölümü — Bilinen kısıtlamalar
4. ✅ Teknik destek ekibi — Çözülemeyen sorunlar

---

## 🎉 Başarılı Kurulum!

Artık SAP ME/MII projelerinizi analiz etmeye hazırsınız!

```powershell
python me_mii_folder_analyzer.py --root "D:/YourProject" --out ./analysis
```

**İyi analizler! 🚀**
