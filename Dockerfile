# Python 3.11 slim image kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY nicegui_app.py .
COPY start.sh .

# Script'i çalıştırılabilir yap
RUN chmod +x start.sh

# Non-root user oluştur (güvenlik için)
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Port 8080'i aç
EXPOSE 8080

# Environment variables (default values)
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=library
ENV DB_USER=postgres
ENV DB_PASSWORD=password

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1

# Uygulamayı çalıştır
CMD ["./start.sh"]
