#!/bin/bash
# Script para actualizar logs desde el contenedor

LOG_FILE="/usr/share/nginx/html/current-logs.txt"
CONTAINER_NAME="coach-motivacional-bot"

# Obtener logs del contenedor
docker logs --tail=1000 --timestamps "$CONTAINER_NAME" > "$LOG_FILE" 2>&1

# Agregar timestamp de actualización
echo "" >> "$LOG_FILE"
echo "# Logs actualizados: $(date)" >> "$LOG_FILE"