# 🍓 Guía de instalación en Raspberry Pi con Disco Externo

## Preparación del disco externo en /mnt/sda1/shared/Projects

### 1. Conectar y verificar el disco externo

```bash
# Verificar discos conectados
lsblk
sudo fdisk -l

# Verificar si ya está montado
df -h | grep sda1
```

### 2. Montar el disco en /mnt/sda1 (si no está montado)

```bash
# Crear punto de montaje
sudo mkdir -p /mnt/sda1

# Montar el disco
sudo mount /dev/sda1 /mnt/sda1

# Verificar montaje
df -h /mnt/sda1
```

### 3. Crear estructura de directorios específica

```bash
# Crear estructura completa en el disco externo
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-data
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs
sudo mkdir -p /mnt/sda1/shared/Projects/ai-coach/coach-bot-backups

# Configurar permisos para el usuario david
sudo chown -R david:david /mnt/sda1/shared/
sudo chmod -R 755 /mnt/sda1/shared/
```

### 4. Configurar montaje automático permanente

```bash
# Obtener UUID del disco para montaje estable
sudo blkid /dev/sda1

# Editar fstab para montaje automático
sudo nano /etc/fstab

# Añadir línea (reemplaza UUID_AQUI con el UUID real):
UUID=UUID_AQUI /mnt/sda1 ext4 defaults,nofail,x-systemd.device-timeout=10 0 2

# Probar montaje automático
sudo umount /mnt/sda1
sudo mount -a
df -h /mnt/sda1
```

## Preparación del sistema Raspberry Pi

### 1. Actualizar el sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar dependencias del sistema

```bash
sudo apt install -y python3-pip python3-venv git sqlite3 screen htop bc curl
```

### 3. Verificar Python

```bash
python3 --version  # Debe ser 3.8 o superior
```

## Instalación del bot en disco externo (/mnt/sda1/shared/Projects)

### Opción A: Instalación automática (Recomendada)

```bash
# Descargar script de instalación
cd /tmp
wget https://raw.githubusercontent.com/tu-repo/install_raspberry_pi.sh
chmod +x install_raspberry_pi.sh

# Ejecutar instalación (detecta automáticamente el disco externo)
./install_raspberry_pi.sh
```

### Opción B: Instalación manual paso a paso

#### 1. Navegar al disco externo y crear proyecto

```bash
# Ir al directorio del disco externo
cd /mnt/sda1/shared/Projects/ai-coach

# Crear directorio del proyecto
mkdir -p coach-motivacional-bot
cd coach-motivacional-bot

# Crear enlace simbólico en home para acceso fácil
ln -s /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot ~/coach-motivacional-bot
```

#### 2. Transferir o crear archivos del proyecto

```bash
# Opción A: Si tienes git configurado
git clone <tu-repositorio> .

# Opción B: Transferir archivos por SCP desde tu computadora
# scp -r coach-motivacional-bot/* david@<ip-raspberry>:/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/

# Opción C: Crear archivos manualmente (ver sección de archivos necesarios)
```

#### 3. Crear entorno virtual en el disco externo

```bash
cd /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. Instalar dependencias Python

```bash
# Actualizar pip
pip install --upgrade pip

# Crear requirements.txt si no existe
cat > requirements.txt << EOF
python-telegram-bot==20.7
groq==0.4.1
python-dotenv==1.0.0
schedule==1.2.0
EOF

# Instalar dependencias
pip install -r requirements.txt
```

#### 5. Configurar variables de entorno

```bash
# Crear archivo .env en el disco externo
cat > .env << EOF
# Configuración del Coach Motivacional Bot
TELEGRAM_BOT_TOKEN=
GROQ_API_KEY=

# Configuración específica para disco externo
DB_PATH=/mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db
LOG_PATH=/mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/
BACKUP_PATH=/mnt/sda1/shared/Projects/ai-coach/coach-bot-backups/
EOF

# Editar con tus tokens reales
nano .env
```

## Configuración para ejecución continua en disco externo

### Opción 1: Usando systemd (Recomendado)

#### Crear servicio del sistema

```bash
sudo nano /etc/systemd/system/coach-bot.service
```

Contenido del archivo (adaptado para disco externo):

```ini
[Unit]
Description=Coach Motivacional Bot
After=network.target
# Esperar a que el disco externo esté montado
RequiresMountsFor=/mnt/sda1

[Service]
Type=simple
User=david
WorkingDirectory=/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
Environment=PATH=/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/.venv/bin
ExecStart=/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/.venv/bin/python telegram_bot_pi.py
Restart=always
RestartSec=10

# Verificar que el disco esté montado antes de iniciar
ExecStartPre=/bin/bash -c 'while [ ! -d "/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot" ]; do sleep 1; done'

[Install]
WantedBy=multi-user.target
```

#### Activar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable coach-bot.service
sudo systemctl start coach-bot.service
```

#### Verificar estado

```bash
sudo systemctl status coach-bot.service
```

#### Ver logs

```bash
sudo journalctl -u coach-bot.service -f
```

### Opción 2: Usando screen (Más simple)

```bash
# Instalar screen si no está instalado
sudo apt install screen

# Ejecutar en background
screen -S coach-bot
cd /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
source .venv/bin/activate
python3 telegram_bot_pi.py

# Presionar Ctrl+A, luego D para desconectar
```

Reconectar a la sesión:

```bash
screen -r coach-bot
```

## Estructura de archivos en el disco externo

### Estructura completa creada:

```
/mnt/sda1/shared/Projects/ai-coach/
├── coach-motivacional-bot/          # Código del bot
│   ├── .venv/                       # Entorno virtual Python
│   ├── .env                         # Variables de entorno
│   ├── telegram_bot_pi.py           # Bot principal (versión Pi)
│   ├── ai_coach.py                  # Lógica de IA
│   ├── database.py                  # Gestión de base de datos
│   ├── groq_models.py               # Configuración de modelos
│   ├── requirements.txt             # Dependencias Python
│   └── scripts/                     # Scripts de gestión
│       ├── monitor.sh               # Monitoreo automático
│       ├── backup.sh                # Backup automático
│       └── mount_external.sh        # Montaje del disco
├── coach-bot-data/                  # Datos persistentes
│   └── coach_bot.db                 # Base de datos SQLite
├── coach-bot-logs/                  # Logs del sistema
│   ├── monitor.log                  # Logs de monitoreo
│   └── backup.log                   # Logs de backup
└── coach-bot-backups/               # Backups automáticos
    └── coach-bot-YYYYMMDD_HHMMSS.tar.gz
```

### Enlace simbólico para acceso fácil:

```bash
# Desde cualquier lugar, puedes acceder con:
cd ~/coach-motivacional-bot  # Apunta a /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
```

## Monitoreo y mantenimiento en disco externo

### Scripts de gestión automática

#### Script de monitoreo (/mnt/sda1/shared/Projects/coach-motivacional-bot/scripts/monitor.sh)

```bash
#!/bin/bash
PROJECT_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot"
LOG_FILE="/mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/monitor.log"

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Verificar que el disco externo esté montado
if [ ! -d "$PROJECT_DIR" ]; then
    log_message "ERROR: Disco externo no montado en /mnt/sda1"
    # Intentar remontar
    sudo mount /dev/sda1 /mnt/sda1 2>/dev/null
    exit 1
fi

# Verificar servicio del bot
if ! systemctl is-active --quiet coach-bot.service; then
    log_message "Servicio inactivo, reiniciando..."
    sudo systemctl restart coach-bot.service
fi

# Verificar espacio en disco externo
DISK_USAGE=$(df /mnt/sda1 | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_message "ADVERTENCIA: Disco externo al $DISK_USAGE% de capacidad"
fi

# Limpiar logs antiguos (mantener últimos 30 días)
find "/mnt/sda1/shared/Projects/ai-coach/coach-bot-logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true
```

#### Script de backup (/mnt/sda1/shared/Projects/coach-motivacional-bot/scripts/backup.sh)

```bash
#!/bin/bash
PROJECT_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot"
BACKUP_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-bot-backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Verificar que el proyecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Proyecto no encontrado en $PROJECT_DIR"
    exit 1
fi

# Crear backup completo
tar -czf "$BACKUP_DIR/coach-bot-$DATE.tar.gz" \
    -C "/mnt/sda1/shared/Projects/ai-coach" \
    --exclude='coach-motivacional-bot/.venv' \
    --exclude='coach-motivacional-bot/__pycache__' \
    coach-motivacional-bot \
    coach-bot-data

# Mantener solo los últimos 14 backups
find "$BACKUP_DIR" -name "coach-bot-*.tar.gz" -mtime +14 -delete

# Log del backup
echo "$(date): Backup creado: coach-bot-$DATE.tar.gz" >> "/mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/backup.log"
```

### Configurar tareas programadas (cron)

```bash
# Editar crontab
crontab -e

# Añadir estas líneas:
# Monitoreo cada 5 minutos
*/5 * * * * /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/monitor.sh

# Backup diario a las 2 AM
0 2 * * * /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/backup.sh

# Verificar montaje del disco al reiniciar
@reboot /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/mount_external.sh
```

## Comandos útiles para gestión en disco externo

### Gestión del bot

```bash
# Acceso rápido al proyecto
cd ~/coach-motivacional-bot

# Ver estado del servicio
sudo systemctl status coach-bot.service

# Reiniciar el bot
sudo systemctl restart coach-bot.service

# Ver logs en tiempo real
sudo journalctl -u coach-bot.service -f

# Ver logs del monitor
tail -f /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/monitor.log
```

### Gestión del disco externo

```bash
# Verificar montaje y espacio
df -h /mnt/sda1

# Ver uso de espacio por directorio
du -sh /mnt/sda1/shared/Projects/*

# Verificar salud del disco
sudo fsck /dev/sda1

# Remontar si es necesario
sudo umount /mnt/sda1
sudo mount /dev/sda1 /mnt/sda1
```

### Mantenimiento de la base de datos

```bash
# Acceder a la base de datos
sqlite3 /mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db

# Backup manual de la base de datos
cp /mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db \
   /mnt/sda1/shared/Projects/ai-coach/coach-bot-backups/manual-backup-$(date +%Y%m%d).db

# Ver tamaño de la base de datos
ls -lh /mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db
```

## Optimizaciones específicas para Raspberry Pi con disco externo

### 1. Configuración de SQLite para disco externo

```bash
# Optimizar SQLite para mejor rendimiento en disco externo
echo "PRAGMA journal_mode=WAL;" | sqlite3 /mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db
echo "PRAGMA synchronous=NORMAL;" | sqlite3 /mnt/sda1/shared/Projects/ai-coach/coach-bot-data/coach_bot.db
```

### 2. Configurar swap en disco externo (si es necesario)

```bash
# Crear archivo swap en disco externo
sudo fallocate -l 1G /mnt/sda1/swapfile
sudo chmod 600 /mnt/sda1/swapfile
sudo mkswap /mnt/sda1/swapfile
sudo swapon /mnt/sda1/swapfile

# Añadir a fstab para montaje automático
echo '/mnt/sda1/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Monitoreo de temperatura y rendimiento

```bash
# Script para monitorear temperatura
cat > /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/temp_monitor.sh << 'EOF'
#!/bin/bash
TEMP=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
echo "$(date): Temperatura CPU: ${TEMP}°C" >> /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/temperature.log

# Alerta si temperatura > 70°C
if (( $(echo "$TEMP > 70" | bc -l) )); then
    echo "$(date): ALERTA - Temperatura alta: ${TEMP}°C" >> /mnt/sda1/shared/Projects/ai-coach/coach-bot-logs/alerts.log
fi
EOF

chmod +x /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/temp_monitor.sh

# Añadir a cron cada 10 minutos
echo "*/10 * * * * /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot/scripts/temp_monitor.sh" | crontab -
```

## Solución de problemas específicos del disco externo

### Disco no se monta automáticamente

```bash
# Verificar fstab
cat /etc/fstab | grep sda1

# Verificar UUID del disco
sudo blkid /dev/sda1

# Probar montaje manual
sudo mount -a

# Ver logs del sistema
sudo journalctl -u systemd-fsck@dev-sda1.service
```

### Bot no inicia después de reinicio

```bash
# Verificar que el disco esté montado
df -h | grep sda1

# Verificar servicio
sudo systemctl status coach-bot.service

# Ver logs de error
sudo journalctl -u coach-bot.service -n 50

# Reiniciar manualmente si es necesario
sudo systemctl restart coach-bot.service
```

### Problemas de permisos en disco externo

```bash
# Verificar permisos
ls -la /mnt/sda1/shared/Projects/

# Corregir permisos si es necesario
sudo chown -R david:david /mnt/sda1/shared/Projects/
sudo chmod -R 755 /mnt/sda1/shared/Projects/
```

## Backup y restauración completa

### Crear backup completo del sistema

```bash
#!/bin/bash
# Script de backup completo
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="coach-bot-complete-$DATE"

# Parar el bot temporalmente
sudo systemctl stop coach-bot.service

# Crear backup completo
tar -czf "/mnt/sda1/shared/Projects/ai-coach/coach-bot-backups/$BACKUP_NAME.tar.gz" \
    -C "/mnt/sda1/shared/Projects/ai-coach" \
    --exclude='coach-motivacional-bot/.venv' \
    --exclude='coach-motivacional-bot/__pycache__' \
    coach-motivacional-bot \
    coach-bot-data \
    coach-bot-logs

# Reiniciar el bot
sudo systemctl start coach-bot.service

echo "Backup completo creado: $BACKUP_NAME.tar.gz"
```

### Restaurar desde backup

```bash
# Parar el bot
sudo systemctl stop coach-bot.service

# Restaurar backup (reemplaza FECHA con la fecha del backup)
cd /mnt/sda1/shared/Projects/ai-coach
tar -xzf coach-bot-backups/coach-bot-complete-FECHA.tar.gz

# Verificar permisos
sudo chown -R david:david /mnt/sda1/shared/Projects/ai-coach/

# Reiniciar el bot
sudo systemctl start coach-bot.service
```

¡Con esta configuración tendrás tu Coach Motivacional ejecutándose de forma robusta y eficiente en tu Raspberry Pi con disco externo! 🚀
