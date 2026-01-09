#!/bin/bash
# -*- coding: utf-8 -*-
# Script de instalación SEGURA con Docker para Raspberry Pi

set -e

echo "🐳 Instalación SEGURA del Coach Motivacional con Docker en Raspberry Pi"
echo "📁 Ubicación: /mnt/sda1/shared/Projects"
echo "=============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# VERIFICACIONES DE SEGURIDAD
echo "🔍 VERIFICACIONES DE SEGURIDAD"
echo "================================"

# Verificar contenedores existentes
EXISTING_CONTAINERS=$(docker ps -a --format "{{.Names}}" | wc -l)
if [ "$EXISTING_CONTAINERS" -gt 0 ]; then
    print_warning "Se encontraron $EXISTING_CONTAINERS contenedores existentes:"
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    read -p "¿Continuar con la instalación? Esto podría afectar contenedores existentes (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Instalación cancelada por el usuario"
        exit 0
    fi
fi

# Verificar Portainer específicamente
if docker ps -a | grep -q portainer; then
    print_warning "Portainer detectado. Creando backup automático..."
    
    # Crear backup de Portainer
    PORTAINER_DATA=$(docker inspect portainer 2>/dev/null | grep -A 10 "Mounts" | grep "Source" | cut -d'"' -f4 | head -1)
    
    if [ ! -z "$PORTAINER_DATA" ] && [ -d "$PORTAINER_DATA" ]; then
        BACKUP_DIR="/tmp/portainer-backup-$(date +%Y%m%d-%H%M%S)"
        sudo cp -r "$PORTAINER_DATA" "$BACKUP_DIR" 2>/dev/null || true
        print_status "Backup de Portainer creado en: $BACKUP_DIR"
        echo "BACKUP_LOCATION=$BACKUP_DIR" > /tmp/portainer_backup_info.txt
    fi
    
    read -p "¿Quieres que el script preserve tu Portainer existente? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        PRESERVE_PORTAINER=true
        print_status "Portainer será preservado"
    else
        PRESERVE_PORTAINER=false
        print_warning "Portainer será reemplazado"
    fi
fi

# Configuración de rutas
EXTERNAL_DRIVE="/mnt/sda1/shared/Projects"
PROJECT_DIR="$EXTERNAL_DRIVE/ai-coach/coach-motivacional-bot"
DATA_DIR="$EXTERNAL_DRIVE/ai-coach/coach-bot-data"
LOGS_DIR="$EXTERNAL_DRIVE/ai-coach/coach-bot-logs"
BACKUPS_DIR="$EXTERNAL_DRIVE/ai-coach/coach-bot-backups"

# Verificar usuario
if [ "$EUID" -eq 0 ]; then
    print_error "No ejecutes este script como root (sudo)"
    exit 1
fi

# Verificar Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "No se detectó Raspberry Pi, continuando..."
fi

# Verificar disco externo
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    print_error "Disco externo no montado en $EXTERNAL_DRIVE"
    echo "Monta el disco primero:"
    echo "  sudo mkdir -p /mnt/sda1"
    echo "  sudo mount /dev/sda1 /mnt/sda1"
    exit 1
fi

print_status "Disco externo detectado en $EXTERNAL_DRIVE"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    echo "Instala Docker primero:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sh get-docker.sh"
    echo "  sudo usermod -aG docker david"
    exit 1
fi

print_status "Docker detectado: $(docker --version)"

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose no encontrado, instalando..."
    sudo apt update
    sudo apt install -y docker-compose
fi

print_status "Docker Compose: $(docker-compose --version)"

# Verificar Portainer
if ! docker ps | grep -q portainer; then
    print_warning "Portainer no está ejecutándose"
    print_info "Para instalar Portainer:"
    echo "  docker volume create portainer_data"
    echo "  docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce"
else
    print_status "Portainer detectado y ejecutándose"
fi

# Crear estructura de directorios
print_status "Creando estructura de directorios..."
mkdir -p "$PROJECT_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$LOGS_DIR"
mkdir -p "$BACKUPS_DIR"
mkdir -p "$PROJECT_DIR/monitor"

# Crear archivos del proyecto
print_status "Creando archivos del proyecto..."

# Dockerfile
cat > "$PROJECT_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim-bullseye

LABEL maintainer="Coach Motivacional Bot"
LABEL description="Bot de Telegram para coaching motivacional personal"
LABEL version="1.0"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd -r botuser && useradd -r -g botuser botuser

RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN mkdir -p /app/data /app/logs /app/backups \
    && chown -R botuser:botuser /app

USER botuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sqlite3; sqlite3.connect('/app/data/coach_bot.db').close()" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python3", "telegram_bot_pi.py"]
EOF

# docker-compose.yml
cat > "$PROJECT_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  coach-bot:
    build: .
    container_name: coach-motivacional-bot
    restart: unless-stopped
    
    environment:
      - TELEGRAM_BOT_TOKEN=\${TELEGRAM_BOT_TOKEN}
      - GROQ_API_KEY=\${GROQ_API_KEY}
      - TZ=Europe/Madrid
    
    env_file:
      - .env
    
    volumes:
      - $DATA_DIR:/app/data
      - $LOGS_DIR:/app/logs
      - $BACKUPS_DIR:/app/backups
    
    networks:
      - coach-network
    
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    labels:
      - "traefik.enable=false"
      - "portainer.group=coaching"
      - "portainer.description=Bot de coaching motivacional personal"

  coach-monitor:
    image: nginx:alpine
    container_name: coach-bot-monitor
    restart: unless-stopped
    
    ports:
      - "8080:80"
    
    volumes:
      - ./monitor/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./monitor/index.html:/usr/share/nginx/html/index.html:ro
      - $LOGS_DIR:/usr/share/nginx/html/logs:ro
    
    networks:
      - coach-network
    
    depends_on:
      - coach-bot
    
    labels:
      - "portainer.group=coaching"
      - "portainer.description=Monitor web para logs del bot"

networks:
  coach-network:
    driver: bridge
    name: coach-network
EOF

# requirements.txt
cat > "$PROJECT_DIR/requirements.txt" << 'EOF'
python-telegram-bot==20.7
groq==0.4.1
python-dotenv==1.0.0
schedule==1.2.0
EOF

# .dockerignore
cat > "$PROJECT_DIR/.dockerignore" << 'EOF'
.venv/
venv/
__pycache__/
*.pyc
.env
*.db
*.log
logs/
backups/
.git/
README.md
*.md
install_*.sh
test_*.py
debug_*.py
EOF

# .env template
cat > "$PROJECT_DIR/.env" << 'EOF'
# Configuración del Coach Motivacional Bot
TELEGRAM_BOT_TOKEN=
GROQ_API_KEY=

# Configuración opcional
TZ=Europe/Madrid
LOG_LEVEL=INFO
EOF

print_warning "Archivo .env creado. DEBES editarlo con tus tokens:"
print_warning "nano $PROJECT_DIR/.env"

# Copiar archivos Python (necesitarás tenerlos)
print_info "Copiando archivos Python del proyecto..."
if [ -f "telegram_bot_pi.py" ]; then
    cp telegram_bot_pi.py "$PROJECT_DIR/"
    cp ai_coach.py "$PROJECT_DIR/"
    cp database.py "$PROJECT_DIR/"
    cp groq_models.py "$PROJECT_DIR/"
    cp docker-entrypoint.sh "$PROJECT_DIR/"
    chmod +x "$PROJECT_DIR/docker-entrypoint.sh"
    print_status "Archivos Python copiados"
else
    print_warning "Archivos Python no encontrados en directorio actual"
    print_info "Deberás copiar manualmente:"
    echo "  - telegram_bot_pi.py"
    echo "  - ai_coach.py" 
    echo "  - database.py"
    echo "  - groq_models.py"
    echo "  - docker-entrypoint.sh"
fi

# Crear archivos del monitor web
print_status "Creando monitor web..."

# nginx.conf para monitor
cat > "$PROJECT_DIR/monitor/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    sendfile on;
    keepalive_timeout 65;
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /logs/ {
            alias /usr/share/nginx/html/logs/;
            autoindex on;
            autoindex_exact_size off;
            autoindex_localtime on;
            add_header Content-Type text/plain;
        }
        
        location /api/status {
            return 200 '{"status": "running", "timestamp": "$time_iso8601"}';
            add_header Content-Type application/json;
        }
    }
}
EOF

# index.html básico para monitor
cat > "$PROJECT_DIR/monitor/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coach Motivacional Bot - Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        .status-online { color: #4CAF50; }
        .status-offline { color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Coach Motivacional Bot</h1>
            <p>Monitor de Estado - Docker en Raspberry Pi</p>
        </div>
        
        <div class="card">
            <h3>📊 Estado del Bot</h3>
            <p>Estado: <span class="status-online">● En línea</span></p>
            <p>Última actualización: <span id="lastUpdate">--</span></p>
            <a href="/logs/" class="btn" target="_blank">📋 Ver Logs</a>
            <a href="http://localhost:9000" class="btn" target="_blank">🐳 Abrir Portainer</a>
        </div>
        
        <div class="card">
            <h3>📋 Acceso Rápido</h3>
            <p>🐳 <strong>Portainer:</strong> <a href="http://localhost:9000" target="_blank">http://localhost:9000</a></p>
            <p>📊 <strong>Monitor:</strong> <a href="http://localhost:8080" target="_blank">http://localhost:8080</a></p>
            <p>📁 <strong>Datos:</strong> /mnt/sda1/shared/Projects/ai-coach/coach-bot-data</p>
        </div>
    </div>
    
    <script>
        document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        setInterval(() => {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        }, 30000);
    </script>
</body>
</html>
EOF

# Crear scripts de gestión
print_status "Creando scripts de gestión..."

# Script de inicio
cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Coach Motivacional Bot..."
cd /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
docker-compose up -d
echo "✅ Bot iniciado. Monitor: http://localhost:8080"
EOF

# Script de parada
cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 Parando Coach Motivacional Bot..."
cd /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
docker-compose down
echo "✅ Bot parado"
EOF

# Script de actualización
cat > "$PROJECT_DIR/update.sh" << 'EOF'
#!/bin/bash
echo "🔄 Actualizando Coach Motivacional Bot..."
cd /mnt/sda1/shared/Projects/ai-coach/coach-motivacional-bot
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo "✅ Bot actualizado"
EOF

# Script de backup
cat > "$PROJECT_DIR/backup.sh" << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/sda1/shared/Projects/ai-coach/coach-bot-backups"
echo "💾 Creando backup..."
docker-compose stop coach-bot
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" /mnt/sda1/shared/Projects/ai-coach/coach-bot-data
docker-compose start coach-bot
echo "✅ Backup creado: backup-$DATE.tar.gz"
EOF

chmod +x "$PROJECT_DIR"/*.sh

print_status "Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. 📝 Configurar tokens:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. 🚀 Iniciar el bot:"
echo "   cd $PROJECT_DIR"
echo "   docker-compose up -d"
echo ""
echo "3. 📊 Acceder al monitor:"
echo "   http://<ip-raspberry>:8080"
echo ""
echo "4. 🐳 Gestionar con Portainer:"
echo "   http://<ip-raspberry>:9000"
echo ""
echo "🔧 Scripts disponibles:"
echo "   $PROJECT_DIR/start.sh    - Iniciar bot"
echo "   $PROJECT_DIR/stop.sh     - Parar bot"
echo "   $PROJECT_DIR/update.sh   - Actualizar bot"
echo "   $PROJECT_DIR/backup.sh   - Crear backup"
echo ""
echo "📁 Estructura creada:"
echo "   📂 Proyecto: $PROJECT_DIR"
echo "   📂 Datos: $DATA_DIR"
echo "   📂 Logs: $LOGS_DIR"
echo "   📂 Backups: $BACKUPS_DIR"
echo ""
print_status "¡Tu Coach Motivacional con Docker está listo! 🐳🚀"

# RESTAURACIÓN POST-INSTALACIÓN
echo ""
echo "🔧 RESTAURACIÓN POST-INSTALACIÓN"
echo "================================="

# Restaurar Portainer si se hizo backup
if [ -f "/tmp/portainer_backup_info.txt" ]; then
    BACKUP_LOCATION=$(cat /tmp/portainer_backup_info.txt | cut -d'=' -f2)
    if [ -d "$BACKUP_LOCATION" ]; then
        print_info "Backup de Portainer encontrado en: $BACKUP_LOCATION"
        echo "Para restaurar tu Portainer anterior:"
        echo "  1. Parar Portainer actual: docker stop portainer && docker rm portainer"
        echo "  2. Restaurar datos: sudo cp -r $BACKUP_LOCATION/* /mnt/sda1/portainer/data/"
        echo "  3. Recrear Portainer: docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v /mnt/sda1/portainer/data:/data portainer/portainer-ce:latest"
    fi
fi

# Información sobre contenedores que podrían haberse perdido
if [ "$EXISTING_CONTAINERS" -gt 0 ]; then
    print_warning "Si perdiste contenedores, puedes:"
    echo "  1. Acceder a Portainer: http://<ip-raspberry>:9000"
    echo "  2. Ir a 'App Templates' para reinstalar servicios comunes"
    echo "  3. Usar 'Stacks' para recrear configuraciones docker-compose"
    echo "  4. Verificar 'Volumes' para recuperar datos existentes"
fi

echo ""
echo "📞 SOPORTE"
echo "=========="
echo "Si tienes problemas:"
echo "  1. Verifica contenedores: docker ps -a"
echo "  2. Verifica volúmenes: docker volume ls"
echo "  3. Logs de Portainer: docker logs portainer"
echo "  4. Reiniciar Docker: sudo systemctl restart docker"