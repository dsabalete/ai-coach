#!/bin/bash
# -*- coding: utf-8 -*-
# Script de entrada para el contenedor Docker

set -e

# Colores para logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar variables de entorno requeridas
check_env_vars() {
    log_info "Verificando variables de entorno..."
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        log_error "TELEGRAM_BOT_TOKEN no está configurado"
        exit 1
    fi
    
    if [ -z "$GROQ_API_KEY" ]; then
        log_error "GROQ_API_KEY no está configurado"
        exit 1
    fi
    
    log_info "Variables de entorno verificadas ✓"
}

# Función para inicializar la base de datos
init_database() {
    log_info "Inicializando base de datos..."
    
    # Crear directorio de datos si no existe y asegurar permisos
    mkdir -p /app/data
    
    # Intentar cambiar permisos si es posible
    if [ -w /app/data ]; then
        log_info "Directorio /app/data tiene permisos de escritura ✓"
    else
        log_warn "Directorio /app/data no tiene permisos de escritura"
        # Intentar crear la base de datos en un directorio temporal
        export DB_PATH="/tmp/coach_bot.db"
        log_info "Usando base de datos temporal en: $DB_PATH"
    fi
    
    # Verificar si la base de datos existe, si no, crearla
    DB_FILE="${DB_PATH:-/app/data/coach_bot.db}"
    if [ ! -f "$DB_FILE" ]; then
        log_info "Creando nueva base de datos en: $DB_FILE"
        python3 -c "
import os
from database import Database
db_path = os.environ.get('DB_PATH', '/app/data/coach_bot.db')
try:
    db = Database(db_path)
    print(f'Base de datos inicializada correctamente en: {db_path}')
except Exception as e:
    print(f'Error creando base de datos: {e}')
    exit(1)
"
    else
        log_info "Base de datos existente encontrada ✓"
    fi
}

# Función para verificar conectividad
check_connectivity() {
    log_info "Verificando conectividad..."
    
    # Verificar conexión a internet
    if ! curl -s --connect-timeout 10 https://api.telegram.org > /dev/null; then
        log_warn "No se puede conectar a Telegram API"
    else
        log_info "Conectividad a Telegram ✓"
    fi
    
    # Verificar conexión a Groq
    if ! curl -s --connect-timeout 10 https://api.groq.com > /dev/null; then
        log_warn "No se puede conectar a Groq API"
    else
        log_info "Conectividad a Groq ✓"
    fi
}

# Función para configurar logging
setup_logging() {
    log_info "Configurando logging..."
    
    # Crear directorio de logs
    mkdir -p /app/logs
    
    # Configurar rotación de logs (solo si tenemos permisos)
    if [ -w /app/logs ]; then
        cat > /app/logs/logrotate.conf << EOF
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 botuser botuser
}
EOF
        log_info "Logging configurado ✓"
    else
        log_warn "No se pueden configurar logs - permisos insuficientes"
    fi
}

# Función para crear backup inicial
create_initial_backup() {
    if [ -f "/app/data/coach_bot.db" ] && [ ! -f "/app/backups/initial_backup.db" ]; then
        log_info "Creando backup inicial..."
        mkdir -p /app/backups
        cp /app/data/coach_bot.db /app/backups/initial_backup.db
        log_info "Backup inicial creado ✓"
    fi
}

# Función para mostrar información del sistema
show_system_info() {
    log_info "=== Información del Sistema ==="
    echo "Fecha: $(date)"
    echo "Usuario: $(whoami)"
    echo "Directorio: $(pwd)"
    echo "Python: $(python3 --version)"
    echo "Espacio disponible: $(df -h /app | tail -1 | awk '{print $4}')"
    
    # Verificar si free está disponible
    if command -v free >/dev/null 2>&1; then
        echo "Memoria disponible: $(free -h | grep Mem | awk '{print $7}')"
    else
        echo "Memoria disponible: No disponible (comando free no encontrado)"
    fi
    
    log_info "================================"
}

# Función principal
main() {
    log_info "🤖 Iniciando Coach Motivacional Bot en Docker"
    
    # Mostrar información del sistema
    show_system_info
    
    # Verificar variables de entorno
    check_env_vars
    
    # Configurar logging
    setup_logging
    
    # Inicializar base de datos
    init_database
    
    # Crear backup inicial
    create_initial_backup
    
    # Verificar conectividad
    check_connectivity
    
    log_info "🚀 Iniciando aplicación..."
    
    # Ejecutar el comando pasado como argumentos
    exec "$@"
}

# Manejar señales para shutdown graceful
trap 'log_info "Recibida señal de shutdown, cerrando aplicación..."; exit 0' SIGTERM SIGINT

# Ejecutar función principal
main "$@"