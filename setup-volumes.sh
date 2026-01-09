#!/bin/bash
# Script para preparar los volúmenes con permisos correctos

echo "Preparando directorios para el bot..."

# Crear directorios si no existen
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-data
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs  
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-backups

# Obtener UID y GID del usuario botuser en el contenedor (1000:1000 por defecto)
BOTUSER_UID=1000
BOTUSER_GID=1000

echo "Configurando permisos para UID:GID $BOTUSER_UID:$BOTUSER_GID"

# Cambiar propietario y permisos
sudo chown -R $BOTUSER_UID:$BOTUSER_GID /mnt/sda1/shared/Projects/ai-coach/coach-bot-data
sudo chown -R $BOTUSER_UID:$BOTUSER_GID /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs
sudo chown -R $BOTUSER_UID:$BOTUSER_GID /mnt/sda1/shared/Projects/ai-coach/coach-bot-backups

sudo chmod -R 755 /mnt/sda1/shared/Projects/ai-coach/coach-bot-data
sudo chmod -R 755 /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs
sudo chmod -R 755 /mnt/sda1/shared/Projects/ai-coach/coach-bot-backups

echo "✓ Directorios preparados correctamente"
echo "Ahora puedes ejecutar: docker-compose up -d"