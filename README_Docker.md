# 🐳 Kütüphane Yönetim Sistemi - Docker Kılavuzu

Bu proje Docker ile tam entegre edilmiş bir kütüphane yönetim sistemidir.

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Docker
- Docker Compose

### Uygulamayı Başlatma

```bash
# Uygulamayı başlat
docker-compose up -d

# Uygulamaya erişim
# http://localhost:8080
```

### Uygulamayı Durdurma

```bash
# Uygulamayı durdur
docker-compose down

# Verileri de silmek için
docker-compose down -v
```

## 📋 Komutlar

### Temel Komutlar

```bash
# Uygulamayı başlat
docker-compose up -d

# Uygulamayı durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f

# Container durumunu kontrol et
docker-compose ps

# Yeniden build et
docker-compose up -d --build
```

### Geliştirme Komutları

```bash
# Sadece uygulamayı yeniden başlat
docker-compose restart app

# Sadece PostgreSQL'i yeniden başlat
docker-compose restart postgres

# Container'a bağlan
docker-compose exec app bash
docker-compose exec postgres psql -U postgres -d library
```

## 🔧 Yapılandırma

### Environment Variables

`.env` dosyası oluşturarak yapılandırmayı özelleştirebilirsiniz:

```env
# Database Configuration
DB_NAME=library
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432

# Application Configuration
APP_PORT=8080
```

### Port Değiştirme

Farklı port kullanmak için:

```bash
# Environment variable ile
APP_PORT=3000 docker-compose up -d

# Veya .env dosyasında
APP_PORT=3000
```

## 📊 Servisler

### PostgreSQL Database
- **Port**: 5432
- **Image**: postgres:16-alpine
- **Volume**: postgres_data
- **Health Check**: ✅

### NiceGUI Application
- **Port**: 8080
- **Image**: Custom Python 3.11
- **Health Check**: ✅
- **Hot Reload**: ✅

## 🔍 Sorun Giderme

### Container Başlamıyor

```bash
# Logları kontrol et
docker-compose logs

# Container'ları yeniden başlat
docker-compose down
docker-compose up -d
```

### Veritabanı Bağlantı Sorunu

```bash
# PostgreSQL durumunu kontrol et
docker-compose logs postgres

# Veritabanına bağlan
docker-compose exec postgres psql -U postgres -d library
```

### Port Çakışması

```bash
# Kullanılan portları kontrol et
netstat -tulpn | grep :8080
netstat -tulpn | grep :5432

# Farklı port kullan
APP_PORT=3000 docker-compose up -d
```

## 🛠️ Geliştirme

### Kod Değişiklikleri

Kod değişiklikleriniz otomatik olarak yansır (hot reload).

### Yeni Bağımlılık Ekleme

1. `requirements.txt` dosyasını güncelleyin
2. Container'ı yeniden build edin:
   ```bash
   docker-compose up -d --build
   ```

### Veritabanı Şeması Değişiklikleri

1. `init.sql` dosyasını güncelleyin
2. Veritabanını sıfırlayın:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## 📈 Production

### Güvenlik

- Non-root user kullanımı
- Environment variables ile şifre yönetimi
- Health checks

### Monitoring

```bash
# Container durumları
docker-compose ps

# Resource kullanımı
docker stats

# Log takibi
docker-compose logs -f
```

## 🎯 Özellikler

- ✅ PostgreSQL veritabanı
- ✅ NiceGUI web arayüzü
- ✅ Otomatik başlatma
- ✅ Health checks
- ✅ Hot reload
- ✅ Volume persistence
- ✅ Network isolation
- ✅ Environment configuration
- ✅ Security best practices

## 📞 Destek

Sorun yaşarsanız:

1. Logları kontrol edin: `docker-compose logs`
2. Container durumunu kontrol edin: `docker-compose ps`
3. Yeniden başlatın: `docker-compose down && docker-compose up -d`
