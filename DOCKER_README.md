# 🐳 SAPDOCAI Docker Setup

SAPDOCAI'yi Docker ile kolayca çalıştırın! Bu setup ile tüm database'ler ve uygulama tek komutla başlatılır.

## 🚀 Hızlı Başlangıç

### 1. Tüm Servisleri Başlatın
```bash
docker-compose up -d
```

### 2. Uygulamaya Erişin
- **SAPDOCAI Web App:** http://localhost:8501
- **MySQL:** localhost:3306
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379
- **MongoDB:** localhost:27017

### 3. Servisleri Durdurun
```bash
docker-compose down
```

## 📊 Database Bağlantı Bilgileri

### MySQL
- **Host:** localhost:3306
- **Database:** sapdocai_db
- **Username:** sapdocai_user
- **Password:** sapdocai_pass
- **Root Password:** sapdocai_root

### PostgreSQL
- **Host:** localhost:5432
- **Database:** sapdocai_pg
- **Username:** sapdocai_user
- **Password:** sapdocai_pass

### Redis
- **Host:** localhost:6379
- **Database:** 0

### MongoDB
- **Host:** localhost:27017
- **Database:** sapdocai_docs
- **Username:** sapdocai_admin
- **Password:** sapdocai_admin_pass

## 🔧 Geliştirme Modu

### Development Setup
```bash
# Development modunda çalıştır (hot reload ile)
docker-compose -f docker-compose.dev.yml up -d

# Logları takip et
docker-compose -f docker-compose.dev.yml logs -f sapdocai-dev
```

### Tek Servis Çalıştırma
```bash
# Sadece SAPDOCAI uygulaması
docker-compose up sapdocai

# Sadece MySQL
docker-compose up mysql

# Sadece PostgreSQL
docker-compose up postgres
```

## 📁 Volume Mounts

Docker container'ları aşağıdaki klasörleri host ile paylaşır:

- `./streamlit_output` → `/app/streamlit_output`
- `./visualization_output` → `/app/visualization_output`
- `./pdf_reports` → `/app/pdf_reports`
- `./Data` → `/app/Data`

## 🗄️ Database Schema

### Analysis Results
```sql
CREATE TABLE analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_files INT DEFAULT 0,
    java_classes INT DEFAULT 0,
    sapui5_views INT DEFAULT 0,
    database_accesses INT DEFAULT 0,
    rest_endpoints INT DEFAULT 0,
    bls_steps INT DEFAULT 0,
    status ENUM('running', 'completed', 'failed') DEFAULT 'running'
);
```

### Java Classes
```sql
CREATE TABLE java_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    class_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    package_name VARCHAR(255),
    methods_count INT DEFAULT 0,
    complexity_score INT DEFAULT 0
);
```

### SAPUI5 Components
```sql
CREATE TABLE sapui5_components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    component_type ENUM('controller', 'view', 'fragment', 'model', 'service'),
    component_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    functions_count INT DEFAULT 0,
    event_handlers_count INT DEFAULT 0,
    api_calls_count INT DEFAULT 0
);
```

## 🔍 Troubleshooting

### Container'lar Başlamıyor
```bash
# Logları kontrol et
docker-compose logs

# Container'ları yeniden başlat
docker-compose restart

# Tüm container'ları temizle ve yeniden başlat
docker-compose down -v
docker-compose up -d
```

### Database Bağlantı Sorunu
```bash
# Database container'larını kontrol et
docker-compose ps

# Database'e bağlan
docker-compose exec mysql mysql -u sapdocai_user -p sapdocai_db
docker-compose exec postgres psql -U sapdocai_user -d sapdocai_pg
```

### Port Çakışması
Eğer portlar kullanımdaysa, `docker-compose.yml` dosyasındaki port numaralarını değiştirin:

```yaml
ports:
  - "8502:8501"  # SAPDOCAI için farklı port
  - "3307:3306"  # MySQL için farklı port
```

## 📈 Monitoring

### Container Durumu
```bash
# Tüm container'ları listele
docker-compose ps

# Resource kullanımı
docker stats

# Logları takip et
docker-compose logs -f
```

### Database Monitoring
```bash
# MySQL performance
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# PostgreSQL activity
docker-compose exec postgres psql -U sapdocai_user -d sapdocai_pg -c "SELECT * FROM pg_stat_activity;"
```

## 🚀 Production Deployment

### Environment Variables
```bash
# .env dosyası oluşturun
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PASSWORD=your_secure_password
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password
```

### Security
- Production'da güçlü şifreler kullanın
- Database portlarını dışarıya açmayın
- SSL/TLS sertifikaları ekleyin
- Firewall kurallarını yapılandırın

## 📚 Daha Fazla Bilgi

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)

---

**🎉 Artık SAPDOCAI'yi Docker ile çalıştırabilirsiniz!**
