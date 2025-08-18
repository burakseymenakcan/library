# Kütüphane Yönetim Sistemi

Modern ve kullanıcı dostu kütüphane yönetim sistemi. NiceGUI ile geliştirilmiş, PostgreSQL veritabanı kullanan, Docker ile kolayca kurulabilen web uygulaması.

## Özellikler

-  **Kullanıcı Yönetimi**: Kayıt, giriş, admin rolleri
-  **Kitap Yönetimi**: Ekleme, düzenleme, arama
-  **Ödünç Alma**: Kitap ödünç alma/iade sistemi
-  **Admin Paneli**: Kullanıcı ve kitap yönetimi
-  **Güvenlik**: Şifre hash'leme, SQL injection koruması

##  Teknolojiler

- **Frontend & Backend**: NiceGUI (Python)
- **Veritabanı**: PostgreSQL 16
- **Containerization**: Docker & Docker Compose

##  Hızlı Başlangıç

### Kurulum

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

2. **Docker ile başlatın:**
```bash
docker-compose up -d
```

3. **Uygulamaya erişin:** http://localhost:8080

### Varsayılan Giriş
- **Kullanıcı adı**: `admin`
- **Şifre**: `admin`

##  Kullanım

###  Normal Kullanıcı
1. Kayıt olun veya giriş yapın
2. Kitap kataloğunu görüntüleyin
3. Kitap arayın ve ödünç alın
4. Ödünç aldığınız kitapları takip edin

###  Admin Kullanıcı
1. Admin hesabıyla giriş yapın
2. Kullanıcı yönetimi yapın
3. Yeni kitaplar ekleyin
4. Ödünç alınanları takip edin

##  Docker Komutları

```bash
# Başlat
docker-compose up -d

# Durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f

# Yeniden build et
docker-compose up -d --build
```

##  Proje Yapısı

```
library-management-system/
├── README.md                 # Bu dosya
├── nicegui_app.py           # Ana uygulama
├── requirements.txt         # Python bağımlılıkları
├── Dockerfile              # Docker yapılandırması
├── docker-compose.yml      # Docker Compose yapılandırması
├── start.sh               # Başlatma scripti
├── init.sql              # Veritabanı başlatma
└── .dockerignore         # Docker ignore dosyası
```

##  Yapılandırma

### Environment Variables
`.env` dosyası oluşturarak yapılandırmayı özelleştirebilirsiniz:

```env
DB_NAME=library
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432
APP_PORT=8080
```

##  Sorun Giderme

### Container Başlamıyor
```bash
docker-compose logs
docker-compose down && docker-compose up -d
```

### Port Çakışması
```bash
APP_PORT=3000 docker-compose up -d
```

##  Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull Request oluşturun

##  Lisans

GNU General Public License v3.0 (GPL-3.0)
