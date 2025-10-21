# 🎓 Teknik Eğitim Materyali - TVMES Projesi

**Oluşturulma Tarihi:** 2025-10-21  
**Geliştirme Özeti:** BaseController refactoring ve servis merkezileştirme  
**Proje:** TVMES (SAP ME/MII Integration)

## 📋 İçindekiler

1. [Mimari Değişiklik Özeti](#mimari-değişiklik-özeti)
2. [Kritik Servis Kullanımı](#kritik-servis-kullanımı)
3. [ME Domain Fonksiyonları](#me-domain-fonksiyonları)
4. [Güvenlik ve En İyi Uygulamalar](#güvenlik-ve-en-iyi-uygulamalar)
5. [Sorun Giderme Rehberi](#sorun-giderme-rehberi)

---

## 🏗️ Mimari Değişiklik Özeti

### Değişiklik Detayları

**Önceki Durum:**
- BaseController'da 91 fonksiyon bulunuyordu
- `onPressDisassemble` ve `onPressAssemble` fonksiyonları BaseController içindeydi
- SFC operasyonları (Start/Complete/Hold) farklı controller'larda dağınık haldeydi

**Yeni Durum:**
- `TraceabilityService` oluşturuldu
- `SfcOperationService` oluşturuldu
- BaseController sadece UI/Routing/Genel durum yönetiminden sorumlu

### Neden Bu Değişiklik Yapıldı?

1. **Sorumluluk Ayrımı (Separation of Concerns)**
   - BaseController'ın karmaşıklığını azaltmak
   - Tek nokta arıza riskini minimize etmek

2. **Yeniden Kullanılabilirlik**
   - Servisler farklı controller'larda kullanılabilir
   - Kod tekrarını önlemek

3. **Test Edilebilirlik**
   - Servisler bağımsız olarak test edilebilir
   - Mock objeler ile unit test yazılabilir

---

## 🔧 Kritik Servis Kullanımı

### TraceabilityService

**Amaç:** Montaj/söküm işlemlerini merkezi olarak yönetmek

**Kullanım Örneği:**
```javascript
// Eski kullanım (BaseController'da)
onPressDisassemble: function() {
    // 50+ satır kod
    // ME API çağrıları
    // Hata yönetimi
    // UI güncellemeleri
}

// Yeni kullanım
onPressDisassemble: function() {
    TraceabilityService.disassembleComponent(this.getView())
        .then(this.onDisassembleSuccess.bind(this))
        .catch(this.onDisassembleError.bind(this));
}
```

**Servis Metodları:**
- `disassembleComponent(view)` - Bileşen sökme
- `assembleComponent(view)` - Bileşen montaj
- `getTraceabilityData(sfcId)` - İzlenebilirlik verisi

### SfcOperationService

**Amaç:** SFC operasyonlarını merkezi olarak yönetmek

**Kullanım Örneği:**
```javascript
// Eski kullanım (farklı controller'larda)
onPressCompleteSFC: function() {
    // Her controller'da farklı implementasyon
}

// Yeni kullanım
onPressCompleteSFC: function() {
    SfcOperationService.completeSFC(this.getSFCId())
        .then(this.onCompleteSFCSuccess.bind(this))
        .catch(this.onCompleteSFCError.bind(this));
}
```

**Servis Metodları:**
- `startSFC(sfcId, operation)` - SFC başlatma
- `completeSFC(sfcId)` - SFC tamamlama
- `holdSFC(sfcId, reason)` - SFC bekletme
- `getSFCStatus(sfcId)` - SFC durumu sorgulama

---

## 🏭 ME Domain Fonksiyonları

### En Sık Kullanılan ME API'ları

| API | Kullanım Sayısı | Amaç | Kullanım Yeri |
|-----|----------------|------|---------------|
| `split` | 63 | SFC bölme işlemi | packageLabel.controller.js |
| `response` | 47 | ME API yanıt işleme | BaseController.js |
| `getSelectedKey` | 28 | Seçili anahtar alma | qualityChain.controller.js |
| `attachChange` | 16 | Değişiklik dinleyicisi | confirmation.controller.js |
| `detachChange` | 4 | Dinleyici kaldırma | BaseController.js |

### Kritik ME Fonksiyonları

#### 1. SFC Operasyonları
```javascript
// SFC başlatma
ME.startSFC(sfcId, operationId)
    .then(response => {
        if (response.success) {
            this.showSuccessMessage("SFC başlatıldı");
        }
    })
    .catch(error => {
        this.showErrorMessage("SFC başlatılamadı: " + error.message);
    });
```

#### 2. Barkod İşlemleri
```javascript
// Barkod okuma ve SFC oluşturma
ME.scanBarcode(barcode)
    .then(response => {
        if (response.sfcId) {
            this.setSFCId(response.sfcId);
        }
    });
```

#### 3. Hata Yönetimi
```javascript
// ME hata kodlarını işleme
ME.handleError(errorCode) {
    switch(errorCode) {
        case '13911':
            return "SFC yanlış operasyonda";
        case '13043':
            return "Yetersiz miktar mevcut";
        default:
            return "Bilinmeyen hata";
    }
}
```

---

## 🛡️ Güvenlik ve En İyi Uygulamalar

### 1. API Güvenliği

**Önceki Durum:**
- Hardcoded kimlik doğrulama
- NC Login Dialog'da güvenlik açıkları

**Yeni Uygulama:**
```javascript
// Güvenli kimlik doğrulama
AuthenticationService.login(credentials)
    .then(token => {
        this.setAuthToken(token);
        this.initializeMEConnection();
    })
    .catch(error => {
        this.showSecurityError("Kimlik doğrulama başarısız");
    });
```

### 2. Input Validasyonu

```javascript
// SFC ID validasyonu
validateSFCId(sfcId) {
    if (!sfcId || sfcId.length < 8) {
        throw new Error("Geçersiz SFC ID");
    }
    return sfcId;
}

// ME API parametrelerini sanitize etme
sanitizeMEParameters(params) {
    return Object.keys(params).reduce((clean, key) => {
        clean[key] = this.escapeHtml(params[key]);
        return clean;
    }, {});
}
```

### 3. WebSocket Güvenliği

```javascript
// Güvenli WebSocket bağlantısı
connectSecureWebSocket() {
    const wsUrl = `wss://${this.getServerUrl()}/ws?token=${this.getAuthToken()}`;
    this.websocket = new WebSocket(wsUrl);
    
    this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (this.validateMessage(data)) {
            this.handleMessage(data);
        }
    };
}
```

---

## 🔧 Sorun Giderme Rehberi

### Sık Karşılaşılan Sorunlar

#### 1. SFC Operasyon Hataları

**Problem:** "SFC is not in queue at operation" (Hata Kodu: 13911)

**Çözüm:**
```javascript
// SFC durumunu kontrol et
SfcOperationService.getSFCStatus(sfcId)
    .then(status => {
        if (status === 'QUEUED') {
            return SfcOperationService.startSFC(sfcId);
        } else {
            throw new Error(`SFC durumu uygun değil: ${status}`);
        }
    });
```

#### 2. WebSocket Bağlantı Sorunları

**Problem:** WebSocket bağlantısı kesiliyor

**Çözüm:**
```javascript
// Otomatik yeniden bağlanma
reconnectWebSocket() {
    setTimeout(() => {
        if (this.websocket.readyState === WebSocket.CLOSED) {
            this.connectWebSocket();
        }
    }, 5000);
}
```

#### 3. ME API Timeout Sorunları

**Problem:** ME API çağrıları timeout oluyor

**Çözüm:**
```javascript
// Timeout ile ME API çağrısı
callMEAPIWithTimeout(apiCall, timeout = 30000) {
    return Promise.race([
        apiCall,
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), timeout)
        )
    ]);
}
```

### Debug Modu

```javascript
// Debug modunu aktifleştir
enableDebugMode() {
    this.debugMode = true;
    console.log("Debug modu aktif");
}

// ME API çağrılarını logla
logMEAPICall(apiName, params, response) {
    if (this.debugMode) {
        console.log(`ME API: ${apiName}`, {
            params: params,
            response: response,
            timestamp: new Date().toISOString()
        });
    }
}
```

---

## 📊 Performans Optimizasyonu

### 1. Lazy Loading

```javascript
// Controller'ları lazy load et
loadController(controllerName) {
    return import(`./controller/${controllerName}.js`)
        .then(module => module.default);
}
```

### 2. Caching Stratejisi

```javascript
// ME API yanıtlarını cache'le
cacheMEResponse(apiName, params, response) {
    const cacheKey = `${apiName}_${JSON.stringify(params)}`;
    this.cache.set(cacheKey, response, 300000); // 5 dakika
}
```

### 3. Memory Management

```javascript
// Event listener'ları temizle
cleanup() {
    this.websocket?.close();
    this.eventBus?.removeAllListeners();
    this.cache?.clear();
}
```

---

## 🎯 Sonraki Adımlar

1. **Servis Testleri Yazma**
   - Unit testler için Jest kullanın
   - Mock objeler ile ME API'larını simüle edin

2. **Dokümantasyon Güncelleme**
   - API dokümantasyonunu güncelleyin
   - Code review checklist'i oluşturun

3. **Performans İzleme**
   - ME API çağrı sürelerini izleyin
   - WebSocket bağlantı durumunu monitör edin

4. **Güvenlik Testleri**
   - Penetration test yapın
   - OWASP Top 10 kontrollerini uygulayın

---

**📞 Destek:** Teknik sorularınız için development team ile iletişime geçin.  
**📚 Kaynaklar:** [SAP ME Documentation](https://help.sap.com/me), [SAPUI5 Best Practices](https://ui5.sap.com/#/topic)