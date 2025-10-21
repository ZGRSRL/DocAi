# Uygulama Özeti (MVP)

## Genel Mimari Bulgular
- Java Sınıf Sayısı: 0
- BLS/Transaction Adım Sayısı: 0
- Tespit Edilen İlişki Sayısı: 0
- Entegrasyon/Uç Nokta Sayısı: 0
- DB Erişim Sinyalleri: 0

## REST/SOAP & Diğer Uç Noktalar (Örnekler)
- (bulunamadı)

## Olası Veritabanı Erişimleri (Heuristik)
- (bulunamadı)

## Önemli Notlar / Riskler (MVP)
- Bu rapor ilk çıkarım sürümüdür ve heuristikler içerir.
- JDBC/SQL çıkarımı ve prepared-statement çözümlemesi geliştirilebilir.
- WSDL/SOAP analizi genişletilebilir (operation/binding detayları, XSD şemaları).
- Java AST için tree-sitter/ANTLR ile doğruluk artırılabilir.


## SAPUI5/Fiori Analizi

### Uygulama Bilgileri
- **App ID:** production
- **Title:** {{appTitle}}
- **Type:** SAPUI5/Fiori
- **Routes:** 9 adet
- **Views:** 10 adet
- **Dependencies:** sap.m, sap.ui.core

### Routing (9 route)
- **appHome:** `:?query:` → home
- **panelView:** `panel:?query:` → panel
- **traceabilityView:** `traceability:?query:` → traceability
- **typeLabelView:** `typeLabel:?query:` → typeLabel
- **repairView:** `repair:?query:` → repair
- **qualityChainView:** `qualityChain:?query:` → qualityChain
- **confirmationView:** `confirmation:?query:` → confirmation
- **transferView:** `transfer:?query:` → transfer
- **packageLabelView:** `packageLabel:?query:` → packageLabel

### Views (10 view)
- **home:** None.Home
- **notFound:** None.NotFound
- **panel:** production.view.panel
- **traceability:** production.view.traceability
- **typeLabel:** production.view.typeLabel
- **repair:** production.view.repair
- **qualityChain:** production.view.qualityChain
- **confirmation:** production.view.confirmation
- **transfer:** production.view.transfer
- **packageLabel:** production.view.packageLabel

