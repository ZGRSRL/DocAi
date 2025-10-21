# Eğitim Dökümanı (MVP)

## Roller ve Görevler
### Operatör
- Tanımlı transaction akışlarını prosedüre uygun başlatır.
- Hata durumunda temel kontrol: bağlantı, parametre, veri kaynağı.

### Süpervizör
- BLS/Transaction akışlarını izler; kritik adımları ve bağımlılıkları bilir.
- Entegrasyon uç noktalarının (REST/SOAP) sağlık takibini koordine eder.

### Admin
- Konfigürasyon dosyaları ve DSN bağlantılarını yönetir.
- Log/izleme sistemlerini ve hata senaryolarını dokümante eder.

## İş Akışı Örnekleri
- [Örnek] Sipariş Oluşturma: REST endpoint → Transaction → BLS Step(Execute SQL) → DB INSERT
- [Örnek] Ürün Takibi: UI → Service → Query → Raporlama

## SSS (Skeleton)
- S: X Transaction hangi tabloyu günceller?  
  C: SUMMARY ve graph.mmd içindeki ilişkilere bakın; DB Inspector genişletmesi gerekebilir.
- S: Y Servisi hangi dış sisteme çağrı yapıyor?  
  C: SUMMARY'de HTTP/URL yakalamalarına ve WSDL adreslerine bakın.

## Sorun Giderme (Skeleton)
- BLS 'Execute SQL' adımı başarısız → DSN/credential, parametre türleri, indeks/lock kontrolü.
- REST 5xx → Bağımlı servis/ERP/IDoc uçları ve ağ izinleri.
- Timeout → Step zincirinde ağır sorgular veya dış sistem gecikmeleri.
