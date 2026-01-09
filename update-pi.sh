#!/bin/bash
# Script para actualizar la aplicación en Raspberry Pi

echo "🔄 Actualizando aplicación en Raspberry Pi..."

# Parar contenedores
docker-compose down

# Hacer pull de los últimos cambios
git pull origin main

# Reconstruir imágenes sin cache
docker-compose build --no-cache

# Limpiar webhook de Telegram
python3 clear_webhook.py

# Esperar para que Telegram libere la conexión
echo "⏳ Esperando 30 segundos para liberar conexión de Telegram..."
sleep 30

# Iniciar contenedores
docker-compose up -d

echo "✅ Actualización completada"
echo "📊 Monitor disponible en: http://$(hostname -I | awk '{print $1}'):8081"
