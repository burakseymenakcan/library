#!/bin/bash

echo "📚 Kütüphane Yönetim Sistemi"
echo "================================"

case "$1" in
    "start")
        echo "🚀 Servisleri başlatılıyor..."
        docker-compose up -d
        echo "✅ Servisler başlatıldı!"
        echo "📚 Kütüphane: http://localhost:8080"
        echo "🗄️ pgAdmin: http://localhost:5050"
        ;;
    "stop")
        echo "🛑 Servisleri durduruluyor..."
        docker-compose down
        echo "✅ Servisler durduruldu!"
        ;;
    "restart")
        echo "🔄 Servisler yeniden başlatılıyor..."
        docker-compose down
        docker-compose up -d
        echo "✅ Servisler yeniden başlatıldı!"
        ;;
    "logs")
        echo "📊 Logları gösteriliyor..."
        docker-compose logs -f
        ;;
    "status")
        echo "📋 Servis durumları:"
        docker-compose ps
        ;;
    *)
        echo "Kullanım: $0 {start|stop|restart|logs|status}"
        echo ""
        echo "Komutlar:"
        echo "  start   - Servisleri başlat"
        echo "  stop    - Servisleri durdur"
        echo "  restart - Servisleri yeniden başlat"
        echo "  logs    - Logları göster"
        echo "  status  - Servis durumlarını göster"
        ;;
esac
