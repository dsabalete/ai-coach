#!/bin/sh
# Script para actualizar logs desde el contenedor

# Usar API version compatible
export DOCKER_API_VERSION=1.41

LOG_FILE="/usr/share/nginx/html/current-logs.txt"
CONTAINER_NAME="coach-motivacional-bot"

# Obtener logs del contenedor (con manejo de errores)
if docker logs --tail=100 --timestamps "$CONTAINER_NAME" > "$LOG_FILE" 2>&1; then
    # Agregar timestamp de actualización
    echo "" >> "$LOG_FILE"
    echo "# Logs actualizados: $(date)" >> "$LOG_FILE"
else
    echo "Error: No se pudieron obtener los logs del contenedor $CONTAINER_NAME" > "$LOG_FILE"
    echo "Fecha: $(date)" >> "$LOG_FILE"
fi

# Asegurar permisos
chmod 644 "$LOG_FILE" 2>/dev/null || true