# Kütüphane Yönetim Sistemi

Bu proje, NiceGUI kullanarak geliştirilmiş modern bir kütüphane yönetim sistemidir.

## 🔧 Özellikler

- ✅ Kullanıcı kayıt ve giriş sistemi
- ✅ Admin rolleri ve kullanıcı yönetimi (banlama, şifre değiştirme)
- ✅ Kitap kataloğu yönetimi (ekleme, düzenleme, arama)
- ✅ Kitap ödünç alma/iade sistemi
- ✅ Admin paneli
- ✅ Modern ve responsive UI
- ✅ Güvenlik: Şifre hash'leme, temel SQL injection korumaları

## 🧰 Teknolojiler

- **Frontend & Backend**: NiceGUI (Python)
- **Veritabanı**: PostgreSQL 16
- **Yönetim Aracı**: pgAdmin 4
- **Containerization**: Docker & Docker Compose

## 🚀 Docker ile Çalıştırma

### Gereksinimler
- Docker
- Docker Compose

### Kurulum ve Çalıştırma

1. Projeyi klonlayın ve dizine gidin:
```bash
cd library
```

2. Kolay başlatma scripti ile servisleri başlatın:
```bash
./start.sh start
```

3. Servislerin durumunu kontrol edin:
```bash
./start.sh status
```

### Erişim Bilgileri

- 📚 Kütüphane Uygulaması: http://localhost:8080
- 🗄️ pgAdmin (Veritabanı Yönetimi): http://localhost:5050

### pgAdmin Giriş Bilgileri
- Email: `admin@admin.com`
- Şifre: `admin`

### pgAdmin'de Veritabanı Bağlantısı
pgAdmin'e giriş yaptıktan sonra:

1. "Add New Server" butonuna tıklayın
2. General sekmesinde: Name: `Library Database`
3. Connection sekmesinde:
   - Host: `postgres` (Docker service name)
   - Port: `5432`
   - Database: `library`
   - Username: `postgres`
   - Password: `password`

### Uygulama Giriş Bilgileri
- Admin Kullanıcı:
  - Kullanıcı Adı: `admin`
  - Şifre: `admin`

## 🛠️ Geliştirme

### Servisleri durdurma
```bash
./start.sh stop
```

### Logları görüntüleme
```bash
./start.sh logs
```

### Servisleri yeniden başlatma
```bash
./start.sh restart
```

### Veritabanını sıfırlama
```bash
docker-compose down -v
./start.sh start
```

## 📁 Proje Yapısı

```
library/
├── nicegui_app.py      # Ana uygulama dosyası
├── Dockerfile          # Docker image tanımı
├── docker-compose.yml  # Docker Compose konfigürasyonu
├── requirements.txt    # Python bağımlılıkları
└── README.md           # Bu dosya
```

## 🐛 Sorun Giderme

### Uygulama başlamıyor
```bash
# Logları kontrol edin
docker-compose logs app

# Servisleri yeniden başlatın
docker-compose restart
```

### Veritabanı bağlantı sorunu
```bash
# PostgreSQL servisinin durumunu kontrol edin
docker-compose logs postgres

# Veritabanını yeniden başlatın
docker-compose restart postgres
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull Request oluşturun

## 🪪 Lisans

GNU General Public License v3.0 (GPL-3.0)
