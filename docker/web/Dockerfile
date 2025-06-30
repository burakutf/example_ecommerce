FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Sistemi güncelle 
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --timeout 100 --retries 10 --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

RUN mkdir -p /app/logs
