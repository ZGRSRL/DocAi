# SAP ME/MII Folder Analyzer — Kurulum Kılavuzu

## Ön Gereksinimler

### 1. Python Kurulumu

Bu araç **Python 3.8 veya üzeri** gerektirir.

#### Python Kurulu mu Kontrol Et:

```powershell
python --version
```

veya

```powershell
python3 --version
```

#### Python Kurulu Değilse:

**Seçenek A: Microsoft Store'dan (Önerilen - Windows 10/11)**
1. Microsoft Store'u açın
2. "Python 3.11" veya "Python 3.12" arayın
3. "Al" veya "Install" butonuna tıklayın

**Seçenek B: python.org'dan**
1. https://www.python.org/downloads/ adresine gidin
2. "Download Python 3.x.x" butonuna tıklayın
3. İndirilen .exe dosyasını çalıştırın
4. **ÖNEMLİ:** "Add Python to PATH" seçeneğini işaretleyin
5. "Install Now" seçeneğini tıklayın

### 2. Bağımlılıkları Yükle

Python kurulduktan sonra, proje klasöründe:

```powershell
# Proje klasörüne git
cd "d:/users/26051677/OneDrive - ARÇELİK A.Ş/ZGRPROJE/DocAı"

# Bağımlılıkları yükle
pip install -r requirements.txt
```

veya

```powershell
python -m pip install -r requirements.txt
```

#### Bağımlılık Listesi:
- `javalang` — Java AST parsing
- `lxml` — XML/XPath parsing
- `networkx` — Graf yapısı
- `pydantic` — Veri modelleme
- `click` — CLI interface
- `rich` — Terminal formatting

## Kullanım

### Temel Kullanım

```powershell
python me_mii_folder_analyzer.py --root "D:/SAP_ME_Project" --out ./out
```

### Parametreler

| Parametre | Açıklama | Varsayılan | Zorunlu |
|-----------|----------|------------|---------|
| `--root` | Analiz edilecek klasör | - | ✅ Evet |
| `--out` | Çıktı klasörü | `./out` | ❌ Hayır |
| `--mermaid` | Mermaid grafik oluştur | `True` | ❌ Hayır |
| `--jsonedges` | JSON kenar dosyası oluştur | `True` | ❌ Hayır |

### Örnek Komutlar

```powershell
# Temel analiz
python me_mii_folder_analyzer.py --root "D:/ME_MII/app" --out ./analysis

# Sadece özet, grafik olmadan
python me_mii_folder_analyzer.py --root "D:/ME_MII/app" --out ./analysis --no-mermaid --no-jsonedges

# Yardım
python me_mii_folder_analyzer.py --help
```

## Test Etme

### 1. Test Klasörü Oluştur

```powershell
# Test klasörü oluştur
mkdir test_project
cd test_project
```

### 2. Örnek Java Dosyası Oluştur

`TestService.java`:
```java
package com.example.service;

import javax.ws.rs.*;
import java.sql.*;

@Path("/api")
public class TestService {
    
    @GET
    @Path("/orders")
    public String getOrders() {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/db");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM orders");
        return "OK";
    }
    
    @POST
    @Path("/orders")
    public String createOrder() {
        // HTTP call example
        String url = "http://external-api.example.com/create";
        return "Created";
    }
}
```

### 3. Örnek XML Dosyası Oluştur

`Transaction.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Transaction>
    <Step Action="ExecuteSQL" Target="DB_QUERY" Name="GetData">
        <Parameter Name="Query" Value="SELECT * FROM products"/>
    </Step>
    <Step Action="CallService" Target="ExternalAPI" Name="SendData">
        <Parameter Name="URL" Value="http://api.example.com/send"/>
    </Step>
</Transaction>
```

### 4. Analizi Çalıştır

```powershell
cd ..
python me_mii_folder_analyzer.py --root ./test_project --out ./test_output
```

### 5. Çıktıları Kontrol Et

```powershell
# Çıktı klasörünü listele
dir test_output

# SUMMARY.md'yi görüntüle
type test_output\SUMMARY.md

# graph.json'u görüntüle
type test_output\graph.json
```

## Sorun Giderme

### Problem: "Python was not found"

**Çözüm:**
1. Python'un kurulu olduğundan emin olun
2. PATH'e eklendiğini kontrol edin:
   ```powershell
   $env:Path
   ```
3. PowerShell'i yeniden başlatın
4. Tam yol ile deneyin:
   ```powershell
   C:\Users\YourUser\AppData\Local\Programs\Python\Python311\python.exe me_mii_folder_analyzer.py --help
   ```

### Problem: "No module named 'javalang'"

**Çözüm:**
```powershell
pip install javalang lxml networkx pydantic click rich
```

### Problem: "Permission denied" veya "Access denied"

**Çözüm:**
1. PowerShell'i yönetici olarak çalıştırın
2. Veya kullanıcı seviyesinde yükleyin:
   ```powershell
   pip install --user -r requirements.txt
   ```

### Problem: Analiz çok yavaş

**Çözüm:**
- Büyük klasörler için alt klasör bazlı analiz yapın
- Gereksiz dosyaları (node_modules, .git, vb.) hariç tutun
- İleride paralel işleme desteği eklenecek

## Güncelleme

Script'i güncellemek için:

```powershell
# Git kullanıyorsanız
git pull

# Manuel güncelleme
# Yeni me_mii_folder_analyzer.py dosyasını indirin ve değiştirin
```

Bağımlılıkları güncellemek için:

```powershell
pip install --upgrade -r requirements.txt
```

## Destek

Sorun yaşarsanız:
1. README.md dosyasını okuyun
2. Script içindeki TODO bölümüne bakın
3. Hata mesajlarını ve log'ları kaydedin
4. Teknik destek ekibiyle iletişime geçin

---

**Not:** Bu MVP sürümüdür. Gelecek versiyonlarda UI, daha gelişmiş parsing ve ek özellikler eklenecektir.
