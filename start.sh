#!/bin/bash

echo "🚀 Kütüphane Yönetim Sistemi başlatılıyor..."
echo "📊 PostgreSQL bağlantısı bekleniyor..."

# PostgreSQL'in hazır olmasını bekle
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME; do
    echo "⏳ PostgreSQL henüz hazır değil, bekleniyor..."
    sleep 2
done

echo "✅ PostgreSQL bağlantısı başarılı!"
echo "🌐 NiceGUI uygulaması başlatılıyor..."

# Uygulamayı çalıştır
exec python nicegui_app.py
