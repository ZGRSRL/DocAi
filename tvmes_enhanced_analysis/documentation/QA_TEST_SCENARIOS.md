# 🧪 QA Test Senaryoları - TVMES Projesi

**Oluşturulma Tarihi:** 2025-10-21  
**Geliştirme Özeti:** BaseController refactoring ve servis merkezileştirme  
**Proje:** TVMES (SAP ME/MII Integration)

## 📋 Test Senaryoları Tablosu

| Test ID | Test Senaryosu | Odak Noktası | İlgili Controller/View | Öncelik | Beklenen Sonuç |
|---------|----------------|--------------|------------------------|---------|-----------------|
| TS_001 | traceabilityView'e gidildikten sonra SFC barkodu okutularak montaj/söküm (disassembleComponent) işleminin başarılı olması | Yeni TraceabilityService'in bütünlüğü | traceability.controller.js | Yüksek | SFC başarıyla sökülür, durum güncellenir |
| TS_002 | qualityChainView'de SFC tamamlama (onPressCompleteSFC) işlemi sırasında, bilinen kritik hata kodu 13911 durumu simüle edildiğinde kullanıcıya özel hata mesajının gelmesi | Yeni Hata İşleme Mantığı | qualityChain.controller.js | Yüksek | Kullanıcıya "SFC yanlış operasyonda" mesajı gösterilir |
| TS_003 | repairView'de, onPressTestNOK işlemi sonrasında WebSocket bağlantısının aktif kalması ve mesaj alıp verebilmesi | WebSocket (keepAliveSession) güvenilirliği | BaseController.js | Orta | WebSocket bağlantısı kesilmez, mesajlar alınır |
| TS_004 | packageLabelView'den Etiket Yazdırma (reprintLabel) işlemi başlatılırken, yeni güvenlik kontrollerinin (OAuth2/SAML varsayılarak) geçilmesi ve kritik bir güvenlik zafiyetinin oluşmaması | Yeni Güvenlik Geliştirmesi | packageLabel.controller.js | Yüksek | Güvenlik kontrolleri başarıyla geçilir |
| TS_005 | BaseController'dan TraceabilityService'e geçiş sonrası, mevcut fonksiyonların geriye dönük uyumluluğunun korunması | Geriye Dönük Uyumluluk | BaseController.js | Yüksek | Eski API çağrıları çalışmaya devam eder |
| TS_006 | SfcOperationService kullanımı sonrası, SFC operasyonlarının (Start/Complete/Hold) tutarlı şekilde çalışması | SFC Operasyon Tutarlılığı | Tüm SFC kullanan controller'lar | Yüksek | Tüm SFC operasyonları başarıyla çalışır |
| TS_007 | WebSocket bağlantısı kesildiğinde, otomatik yeniden bağlanma mekanizmasının çalışması | WebSocket Yeniden Bağlanma | BaseController.js | Orta | 5 saniye içinde otomatik yeniden bağlanır |
| TS_008 | ME API çağrılarında timeout durumunda, kullanıcıya uygun hata mesajının gösterilmesi | ME API Timeout Yönetimi | Tüm ME API kullanan controller'lar | Orta | "İşlem zaman aşımına uğradı" mesajı gösterilir |
| TS_009 | Yeni servis yapısında, hata durumlarında detaylı log kayıtlarının tutulması | Log Kayıt Tutarlılığı | Tüm servisler | Düşük | Hata logları detaylı şekilde kaydedilir |
| TS_010 | Performans testi: 100 eşzamanlı SFC operasyonu sırasında sistemin kararlı kalması | Performans ve Kararlılık | Tüm sistem | Yüksek | Sistem kararlı kalır, yanıt süreleri kabul edilebilir |

---

## 🔍 Detaylı Test Senaryoları

### TS_001: TraceabilityService Montaj/Söküm Testi

**Test Adımları:**
1. Uygulamayı başlat ve traceabilityView'e git
2. Geçerli bir SFC barkodu okut
3. "Söküm" butonuna tıkla
4. TraceabilityService.disassembleComponent() çağrısını doğrula
5. SFC durumunun güncellendiğini kontrol et

**Beklenen Sonuç:**
- SFC başarıyla sökülür
- UI'da başarı mesajı gösterilir
- SFC durumu "Sökülmüş" olarak güncellenir

**Hata Durumları:**
- Geçersiz SFC barkodu: "Geçersiz barkod" mesajı
- SFC zaten sökülmüş: "SFC zaten sökülmüş" mesajı
- ME API hatası: "Söküm işlemi başarısız" mesajı

---

### TS_002: Kritik Hata Kodu 13911 Testi

**Test Adımları:**
1. qualityChainView'e git
2. SFC tamamlama işlemini başlat
3. ME API'dan 13911 hata kodunu simüle et
4. Hata mesajının gösterildiğini kontrol et
5. Kullanıcıya özel açıklama yapıldığını doğrula

**Beklenen Sonuç:**
- "SFC yanlış operasyonda" mesajı gösterilir
- Kullanıcıya çözüm önerisi sunulur
- SFC durumu değişmez

**Hata Durumları:**
- Genel hata mesajı gösterilirse: FAIL
- Kullanıcı yönlendirmesi yapılmazsa: FAIL

---

### TS_003: WebSocket Bağlantı Testi

**Test Adımları:**
1. repairView'e git
2. onPressTestNOK işlemini başlat
3. WebSocket bağlantısının aktif olduğunu kontrol et
4. Test mesajı gönder
5. Yanıt alındığını doğrula

**Beklenen Sonuç:**
- WebSocket bağlantısı aktif kalır
- Mesajlar başarıyla alınır ve gönderilir
- Bağlantı durumu "Bağlı" olarak gösterilir

**Hata Durumları:**
- WebSocket bağlantısı kesilirse: FAIL
- Mesaj alışverişi çalışmazsa: FAIL

---

### TS_004: Güvenlik Kontrol Testi

**Test Adımları:**
1. packageLabelView'e git
2. Etiket yazdırma işlemini başlat
3. OAuth2/SAML kimlik doğrulamasını simüle et
4. Güvenlik kontrollerinin geçildiğini doğrula
5. Yetkisiz erişim denemesini test et

**Beklenen Sonuç:**
- Güvenlik kontrolleri başarıyla geçilir
- Yetkisiz erişim engellenir
- Güvenlik logları kaydedilir

**Hata Durumları:**
- Güvenlik kontrolleri atlanırsa: CRITICAL
- Yetkisiz erişim izin verilirse: CRITICAL

---

### TS_005: Geriye Dönük Uyumluluk Testi

**Test Adımları:**
1. Eski API çağrılarını kullanan test scripti çalıştır
2. BaseController'daki eski fonksiyonları test et
3. Yeni servis yapısının eski çağrıları desteklediğini doğrula
4. Deprecated uyarılarının gösterildiğini kontrol et

**Beklenen Sonuç:**
- Eski API çağrıları çalışmaya devam eder
- Deprecated uyarıları gösterilir
- Yeni servis yapısı kullanılmaya teşvik edilir

---

### TS_006: SFC Operasyon Tutarlılık Testi

**Test Adımları:**
1. Farklı controller'larda SFC operasyonlarını test et
2. Start/Complete/Hold işlemlerinin tutarlı çalıştığını doğrula
3. SfcOperationService'in tüm operasyonları desteklediğini kontrol et
4. Hata durumlarının tutarlı yönetildiğini doğrula

**Beklenen Sonuç:**
- Tüm SFC operasyonları tutarlı çalışır
- Hata yönetimi standartlaştırılmıştır
- Performans iyileştirilmiştir

---

### TS_007: WebSocket Yeniden Bağlanma Testi

**Test Adımları:**
1. WebSocket bağlantısını manuel olarak kes
2. Otomatik yeniden bağlanma mekanizmasını gözlemle
3. 5 saniye içinde yeniden bağlandığını doğrula
4. Mesaj alışverişinin devam ettiğini kontrol et

**Beklenen Sonuç:**
- 5 saniye içinde otomatik yeniden bağlanır
- Mesaj alışverişi kesintisiz devam eder
- Kullanıcıya bağlantı durumu bildirilir

---

### TS_008: ME API Timeout Testi

**Test Adımları:**
1. ME API çağrısını yavaşlat (simüle et)
2. Timeout süresini aşmasını bekle
3. Kullanıcıya timeout mesajının gösterildiğini doğrula
4. Retry mekanizmasının çalıştığını kontrol et

**Beklenen Sonuç:**
- "İşlem zaman aşımına uğradı" mesajı gösterilir
- Retry butonu sunulur
- Sistem kararlı kalır

---

### TS_009: Log Kayıt Tutarlılık Testi

**Test Adımları:**
1. Hata durumu oluştur
2. Log dosyalarını kontrol et
3. Detaylı hata bilgilerinin kaydedildiğini doğrula
4. Log formatının tutarlı olduğunu kontrol et

**Beklenen Sonuç:**
- Hata logları detaylı kaydedilir
- Log formatı tutarlıdır
- Debug bilgileri mevcuttur

---

### TS_010: Performans ve Kararlılık Testi

**Test Adımları:**
1. 100 eşzamanlı SFC operasyonu başlat
2. Sistem kaynaklarını monitör et
3. Yanıt sürelerini ölç
4. Hata oranını kontrol et

**Beklenen Sonuç:**
- Sistem kararlı kalır
- Yanıt süreleri < 2 saniye
- Hata oranı < %1

---

## 🚨 Kritik Test Senaryoları

### Yüksek Öncelikli Testler
- **TS_001**: TraceabilityService bütünlüğü
- **TS_002**: Kritik hata yönetimi
- **TS_004**: Güvenlik kontrolleri
- **TS_005**: Geriye dönük uyumluluk
- **TS_006**: SFC operasyon tutarlılığı
- **TS_010**: Performans ve kararlılık

### Orta Öncelikli Testler
- **TS_003**: WebSocket bağlantı güvenilirliği
- **TS_007**: WebSocket yeniden bağlanma
- **TS_008**: ME API timeout yönetimi

### Düşük Öncelikli Testler
- **TS_009**: Log kayıt tutarlılığı

---

## 📊 Test Metrikleri

### Başarı Kriterleri
- **Fonksiyonel Testler**: %100 başarı
- **Güvenlik Testleri**: %100 başarı
- **Performans Testleri**: Yanıt süresi < 2 saniye
- **Kararlılık Testleri**: Hata oranı < %1

### Test Ortamı Gereksinimleri
- **SAP ME Sistemi**: Test ortamı
- **WebSocket Sunucusu**: Yerel test sunucusu
- **Test Verileri**: SFC, Operasyon, Kullanıcı verileri
- **Monitoring Araçları**: Log analiz araçları

---

## 🔧 Test Otomasyonu

### Otomatik Test Scriptleri
```javascript
// Jest test örneği
describe('TraceabilityService', () => {
    test('should disassemble component successfully', async () => {
        const result = await TraceabilityService.disassembleComponent(mockView);
        expect(result.success).toBe(true);
    });
});
```

### CI/CD Entegrasyonu
- Her commit'te otomatik test çalıştırma
- Test sonuçlarını raporlama
- Başarısız testlerde deployment engelleme

---

**📞 Test Desteği:** QA ekibi ile iletişime geçin  
**📚 Kaynaklar:** [Test Automation Guide](https://jestjs.io/docs/getting-started), [SAP ME Testing](https://help.sap.com/me)