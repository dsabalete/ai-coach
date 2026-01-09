#!/bin/bash
# -*- coding: utf-8 -*-
# Script de instalación automática para Raspberry Pi con disco externo

set -e  # Salir si hay errores

echo "🍓 Instalación del Coach Motivacional en Raspberry Pi"
echo "📁 Ubicación: /mnt/sda1/shared/Projects"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuración de rutas
EXTERNAL_DRIVE="/mnt/sda1/shared/Projects"
PROJECT_DIR="$EXTERNAL_DRIVE/ai-coach/coach-motivacional-bot"
HOME_LINK="$HOME/coach-motivacional-bot"

# Verificar si es Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "No se detectó Raspberry Pi, continuando de todas formas..."
fi

# Verificar usuario
if [ "$EUID" -eq 0 ]; then
    print_error "No ejecutes este script como root (sudo)"
    exit 1
fi

# Verificar que el disco externo esté montado
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    print_error "El disco externo no está montado en $EXTERNAL_DRIVE"
    echo "Verifica que el disco esté conectado y montado correctamente:"
    echo "  sudo mkdir -p /mnt/sda1"
    echo "  sudo mount /dev/sda1 /mnt/sda1"
    echo "  sudo chown -R $USER:$USER /mnt/sda1/shared"
    exit 1
fi

print_status "Disco externo detectado en $EXTERNAL_DRIVE"

# Verificar permisos de escritura
if [ ! -w "$EXTERNAL_DRIVE" ]; then
    print_error "Sin permisos de escritura en $EXTERNAL_DRIVE"
    echo "Ejecuta: sudo chown -R $USER:$USER $EXTERNAL_DRIVE"
    exit 1
fi

print_status "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

print_status "Instalando dependencias del sistema..."
sudo apt install -y python3-pip python3-venv git sqlite3 screen htop bc

# Verificar Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python detectado: $PYTHON_VERSION"

if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    print_status "Versión de Python compatible"
else
    print_error "Se requiere Python 3.8 o superior"
    exit 1
fi

# Crear directorio del proyecto en disco externo
print_status "Creando directorio del proyecto en disco externo..."
mkdir -p "$PROJECT_DIR"

# Crear enlace simbólico en home para facilidad de acceso
if [ ! -L "$HOME_LINK" ]; then
    print_status "Creando enlace simbólico en home..."
    ln -s "$PROJECT_DIR" "$HOME_LINK"
fi

cd "$PROJECT_DIR"

# Crear entorno virtual
print_status "Creando entorno virtual en disco externo..."
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias Python
print_status "Instalando dependencias Python..."
pip install --upgrade pip

# Crear requirements.txt si no existe
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
python-telegram-bot==20.7
groq==0.4.1
python-dotenv==1.0.0
schedule==1.2.0
EOF
fi

pip install -r requirements.txt

# Configurar archivo .env
print_status "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Configuración del Coach Motivacional Bot
TELEGRAM_BOT_TOKEN=
GROQ_API_KEY=

# Configuración específica para disco externo
DB_PATH=$PROJECT_DIR/coach_bot.db
LOG_PATH=$PROJECT_DIR/logs/
BACKUP_PATH=$PROJECT_DIR/backups/
EOF
    print_warning "Archivo .env creado. DEBES editarlo con tus tokens:"
    print_warning "nano $PROJECT_DIR/.env"
fi

# Crear directorios necesarios
print_status "Creando estructura de directorios..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/backups"
mkdir -p "$PROJECT_DIR/scripts"

# Crear servicio systemd con rutas del disco externo
print_status "Configurando servicio del sistema..."
sudo tee /etc/systemd/system/coach-bot.service > /dev/null << EOF
[Unit]
Description=Coach Motivacional Bot
After=network.target
# Esperar a que el disco externo esté montado
RequiresMountsFor=/mnt/sda1

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/.venv/bin
ExecStart=$PROJECT_DIR/.venv/bin/python telegram_bot_pi.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Configuración específica para disco externo
ExecStartPre=/bin/bash -c 'while [ ! -d "$PROJECT_DIR" ]; do sleep 1; done'

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
sudo systemctl daemon-reload

# Crear script de monitoreo optimizado para disco externo
print_status "Creando script de monitoreo..."
cat > "$PROJECT_DIR/scripts/monitor.sh" << 'EOF'
#!/bin/bash
# Script de monitoreo del bot en disco externo
PROJECT_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Verificar que el disco externo esté montado
if [ ! -d "$PROJECT_DIR" ]; then
    log_message "ERROR: Disco externo no montado en /mnt/sda1"
    exit 1
fi

# Verificar si el servicio está activo
if ! systemctl is-active --quiet coach-bot.service; then
    log_message "Servicio inactivo, reiniciando..."
    sudo systemctl restart coach-bot.service
    log_message "Servicio reiniciado"
fi

# Verificar uso de memoria (reiniciar si usa más del 80%)
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEM_USAGE" -gt 80 ]; then
    log_message "Uso de memoria alto ($MEM_USAGE%), reiniciando servicio..."
    sudo systemctl restart coach-bot.service
fi

# Verificar espacio en disco externo
DISK_USAGE=$(df /mnt/sda1 | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_message "ADVERTENCIA: Disco externo al $DISK_USAGE% de capacidad"
fi

# Verificar temperatura (solo en Raspberry Pi)
if command -v vcgencmd &> /dev/null; then
    TEMP=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
    if (( $(echo "$TEMP > 70" | bc -l) )); then
        log_message "Temperatura alta: ${TEMP}°C"
    fi
fi

# Limpiar logs antiguos (mantener últimos 30 días)
find "$PROJECT_DIR/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true
EOF

chmod +x "$PROJECT_DIR/scripts/monitor.sh"

# Crear script de backup optimizado para disco externo
print_status "Creando script de backup..."
cat > "$PROJECT_DIR/scripts/backup.sh" << 'EOF'
#!/bin/bash
# Script de backup automático en disco externo
PROJECT_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Verificar que el proyecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Proyecto no encontrado en $PROJECT_DIR"
    exit 1
fi

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Crear backup (excluyendo entorno virtual y caches)
tar -czf "$BACKUP_DIR/coach-bot-$DATE.tar.gz" \
    -C "$(dirname "$PROJECT_DIR")" \
    --exclude='coach-motivacional-bot/.venv' \
    --exclude='coach-motivacional-bot/__pycache__' \
    --exclude='coach-motivacional-bot/*.pyc' \
    --exclude='coach-motivacional-bot/logs/*.log' \
    coach-motivacional-bot

# Mantener solo los últimos 14 backups (más espacio en disco externo)
find "$BACKUP_DIR" -name "coach-bot-*.tar.gz" -mtime +14 -delete

# Log del backup
echo "$(date): Backup creado: coach-bot-$DATE.tar.gz" >> "$PROJECT_DIR/logs/backup.log"

# Verificar integridad del backup
if tar -tzf "$BACKUP_DIR/coach-bot-$DATE.tar.gz" > /dev/null 2>&1; then
    echo "$(date): Backup verificado correctamente" >> "$PROJECT_DIR/logs/backup.log"
else
    echo "$(date): ERROR: Backup corrupto" >> "$PROJECT_DIR/logs/backup.log"
fi
EOF

chmod +x "$PROJECT_DIR/scripts/backup.sh"

# Crear script de montaje automático del disco
print_status "Creando script de montaje automático..."
cat > "$PROJECT_DIR/scripts/mount_external.sh" << 'EOF'
#!/bin/bash
# Script para montar automáticamente el disco externo

DEVICE="/dev/sda1"
MOUNT_POINT="/mnt/sda1"

# Verificar si el dispositivo existe
if [ ! -b "$DEVICE" ]; then
    echo "Dispositivo $DEVICE no encontrado"
    exit 1
fi

# Crear punto de montaje si no existe
sudo mkdir -p "$MOUNT_POINT"

# Montar si no está montado
if ! mountpoint -q "$MOUNT_POINT"; then
    echo "Montando $DEVICE en $MOUNT_POINT..."
    sudo mount "$DEVICE" "$MOUNT_POINT"
    
    # Configurar permisos
    sudo chown -R david:david "$MOUNT_POINT/shared" 2>/dev/null || true
    
    echo "Disco montado correctamente"
else
    echo "Disco ya está montado"
fi
EOF

chmod +x "$PROJECT_DIR/scripts/mount_external.sh"

# Configurar cron jobs con rutas del disco externo
print_status "Configurando tareas programadas..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/scripts/monitor.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/scripts/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "@reboot $PROJECT_DIR/scripts/mount_external.sh") | crontab -

# Configurar montaje automático en fstab (opcional)
print_status "Configurando montaje automático en fstab..."
if ! grep -q "/dev/sda1" /etc/fstab; then
    echo "/dev/sda1 /mnt/sda1 ext4 defaults,nofail,x-systemd.device-timeout=10 0 2" | sudo tee -a /etc/fstab
    print_status "Entrada añadida a /etc/fstab para montaje automático"
fi

print_status "Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Editar archivo de configuración:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Añadir tus tokens:"
echo "   TELEGRAM_BOT_TOKEN=tu_token_aqui"
echo "   GROQ_API_KEY=tu_api_key_aqui"
echo ""
echo "3. Probar la configuración:"
echo "   cd $PROJECT_DIR && source .venv/bin/activate && python3 test_groq.py"
echo ""
echo "4. Iniciar el servicio:"
echo "   sudo systemctl enable coach-bot.service"
echo "   sudo systemctl start coach-bot.service"
echo ""
echo "5. Verificar estado:"
echo "   sudo systemctl status coach-bot.service"
echo ""
echo "🔧 Comandos útiles:"
echo "   Acceso rápido: cd ~/coach-motivacional-bot (enlace simbólico)"
echo "   Ver logs: sudo journalctl -u coach-bot.service -f"
echo "   Logs del monitor: tail -f $PROJECT_DIR/logs/monitor.log"
echo "   Reiniciar: sudo systemctl restart coach-bot.service"
echo "   Backup manual: $PROJECT_DIR/scripts/backup.sh"
echo ""
echo "📁 Estructura en disco externo:"
echo "   Proyecto: $PROJECT_DIR"
echo "   Logs: $PROJECT_DIR/logs/"
echo "   Backups: $PROJECT_DIR/backups/"
echo "   Scripts: $PROJECT_DIR/scripts/"
echo ""
print_status "¡Tu Raspberry Pi con disco externo está lista para ser un coach 24/7! 🚀"