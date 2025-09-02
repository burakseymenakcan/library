# Python 3.11 slim image kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Add signal handling for graceful shutdown
RUN echo '#!/bin/bash\n\
echo "🛑 Shutting down gracefully..."\n\
python nicegui_app.py &\n\
PID=$!\n\
trap "echo \"🔄 Stopping application...\"; kill $PID; wait $PID; echo \"✅ Application stopped\"; exit 0" SIGTERM SIGINT\n\
wait $PID' > /app/start.sh && chmod +x /app/start.sh

# Run the application with graceful shutdown
CMD ["/app/start.sh"]
