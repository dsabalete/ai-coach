#!/bin/sh
# Script para obtener información real del sistema y del bot

CONTAINER_NAME="coach-motivacional-bot"
OUTPUT_FILE="/usr/share/nginx/html/system-info.json"

#!/bin/sh
# Script para obtener información real del sistema y del bot

CONTAINER_NAME="coach-motivacional-bot"
OUTPUT_FILE="/usr/share/nginx/html/system-info.json"

# Función para obtener información del contenedor
get_container_info() {
    # Usar API version compatible
    export DOCKER_API_VERSION=1.41
    
    local container_id=$(docker ps -q -f name=$CONTAINER_NAME 2>/dev/null)
    
    if [ -z "$container_id" ]; then
        echo "\"container\": {
        \"status\": \"not_found\",
        \"uptime\": \"N/A\",
        \"cpu_usage\": \"N/A\",
        \"memory_usage\": \"N/A\",
        \"memory_percent\": \"N/A\"
    }"
        return
    fi
    
    # Obtener estadísticas del contenedor (simplificado para evitar errores de API)
    local status=$(docker inspect --format='{{.State.Status}}' $container_id 2>/dev/null || echo "unknown")
    
    echo "\"container\": {
        \"status\": \"$status\",
        \"uptime\": \"Running\",
        \"cpu_usage\": \"N/A\",
        \"memory_usage\": \"N/A\",
        \"memory_percent\": \"N/A\"
    }"
}

# Función para obtener información del sistema host
get_host_info() {
    # Uso de memoria del sistema
    local mem_info=$(free -h | grep Mem)
    local mem_total=$(echo "$mem_info" | awk '{print $2}')
    local mem_used=$(echo "$mem_info" | awk '{print $3}')
    local mem_available=$(echo "$mem_info" | awk '{print $7}')
    
    # Uso de disco
    local disk_info=$(df -h / | tail -1)
    local disk_used=$(echo "$disk_info" | awk '{print $5}')
    local disk_available=$(echo "$disk_info" | awk '{print $4}')
    
    # Temperatura CPU (multi-plataforma)
    local cpu_temp="N/A"
    
    # Raspberry Pi / Linux
    if [ -f /host/sys/class/thermal/thermal_zone0/temp ]; then
        local temp_raw=$(cat /host/sys/class/thermal/thermal_zone0/temp 2>/dev/null)
        if [ -n "$temp_raw" ] && [ "$temp_raw" -gt 0 ]; then
            cpu_temp="$((temp_raw / 1000))°C"
        fi
    # Raspberry Pi con vcgencmd
    elif command -v vcgencmd >/dev/null 2>&1; then
        cpu_temp=$(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 || echo "N/A")
    # macOS (desde host)
    elif command -v sysctl >/dev/null 2>&1; then
        # Intentar obtener temperatura de macOS (requiere sensores específicos)
        cpu_temp=$(sysctl -n machdep.xcpm.cpu_thermal_state 2>/dev/null | awk '{print $1"°C"}' || echo "N/A")
    fi
    
    # Load average
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^ *//')
    
    echo "\"host\": {
        \"memory_total\": \"$mem_total\",
        \"memory_used\": \"$mem_used\",
        \"memory_available\": \"$mem_available\",
        \"disk_usage\": \"$disk_used\",
        \"disk_available\": \"$disk_available\",
        \"cpu_temp\": \"$cpu_temp\",
        \"load_average\": \"$load_avg\"
    }"
}

# Función para obtener información de la base de datos
get_database_info() {
    # Usar API version compatible
    export DOCKER_API_VERSION=1.41
    
    # Intentar obtener información de la base de datos desde el contenedor
    local db_info=$(docker exec $CONTAINER_NAME python3 -c "
import sqlite3
import os
try:
    db_path = os.environ.get('DB_PATH', '/app/data/coach_bot.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Contar usuarios
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    # Contar objetivos
    cursor.execute('SELECT COUNT(*) FROM goals')
    goal_count = cursor.fetchone()[0]
    
    # Contar mensajes (usar daily_progress en lugar de messages)
    cursor.execute('SELECT COUNT(*) FROM daily_progress')
    message_count = cursor.fetchone()[0]
    
    conn.close()
    print(f'{user_count},{goal_count},{message_count}')
except Exception as e:
    print('0,0,0')
" 2>/dev/null)
    
    if [ -n "$db_info" ]; then
        local users=$(echo "$db_info" | cut -d',' -f1)
        local goals=$(echo "$db_info" | cut -d',' -f2)
        local messages=$(echo "$db_info" | cut -d',' -f3)
    else
        local users="N/A"
        local goals="N/A"
        local messages="N/A"
    fi
    
    echo "\"database\": {
        \"users\": \"$users\",
        \"goals\": \"$goals\",
        \"progress_entries\": \"$messages\"
    }"
}

# Generar JSON con toda la información
{
    echo "{"
    echo "\"timestamp\": \"$(date -Iseconds)\","
    get_container_info
    echo ","
    get_host_info
    echo ","
    get_database_info
    echo "}"
} > "$OUTPUT_FILE"

# Hacer el archivo legible por nginx
chmod 644 "$OUTPUT_FILE"