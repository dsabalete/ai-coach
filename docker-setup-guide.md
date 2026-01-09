# 🐳 Guía de instalación con Docker y Portainer

## ⚠️ IMPORTANTE: Verificación previa

**ANTES de ejecutar cualquier script de instalación, ejecuta estos comandos:**

```bash
# Verificar contenedores existentes
docker ps -a

# Verificar volúmenes existentes
docker volume ls

# Verificar redes existentes
docker network ls

# Hacer backup de Portainer si existe
if docker ps -a | grep -q portainer; then
    echo "⚠️  Portainer detectado. Haciendo backup..."
    docker run --rm -v portainer_data:/data -v /tmp:/backup alpine tar czf /backup/portainer-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data . 2>/dev/null || echo "Backup con volumen falló, verificando bind mount..."

    # Si usa bind mount, hacer backup diferente
    PORTAINER_DATA=$(docker inspect portainer | grep -A 10 "Mounts" | grep "Source" | cut -d'"' -f4)
    if [ ! -z "$PORTAINER_DATA" ]; then
        sudo cp -r "$PORTAINER_DATA" "/tmp/portainer-backup-$(date +%Y%m%d-%H%M%S)"
        echo "✅ Backup creado en /tmp/portainer-backup-$(date +%Y%m%d-%H%M%S)"
    fi
fi
```

## Ventajas de usar Docker en Raspberry Pi

✅ **Gestión visual** con Portainer - Interfaz web intuitiva  
✅ **Actualizaciones fáciles** - Un clic para actualizar  
✅ **Aislamiento** - El bot no afecta el sistema  
✅ **Backups automáticos** - Volúmenes persistentes  
✅ **Monitoreo integrado** - Logs y métricas en tiempo real  
✅ **Escalabilidad** - Fácil añadir más servicios

## Preparación del disco externo

### 1. Crear estructura de directorios

```bash
# Crear directorios en el disco externo
sudo mkdir -p /mnt/sda1/shared/Projects/coach-bot-data
sudo mkdir -p /mnt/sda1/shared/Projects/coach-bot-logs
sudo mkdir -p /mnt/sda1/shared/Projects/coach-bot-backups
sudo mkdir -p /mnt/sda1/shared/Projects/coach-motivacional-bot

# Configurar permisos
sudo chown -R david:david /mnt/sda1/shared/Projects/
```

### 2. Verificar Docker y Portainer

```bash
# Verificar que Docker está instalado
docker --version

# Verificar que Portainer está ejecutándose
docker ps | grep portainer
```

## Instalación del bot con Docker

### ⚠️ Verificación de seguridad OBLIGATORIA

**NUNCA ejecutes scripts de instalación sin verificar primero:**

```bash
# 1. Verificar qué tienes ejecutándose
docker ps -a
docker volume ls
docker network ls

# 2. Hacer backup de Portainer si existe
./backup_portainer.sh  # (script incluido abajo)

# 3. Anotar qué servicios tienes para restaurar después
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

### Script de backup de Portainer

Crea este script ANTES de cualquier instalación:

```bash
# Crear script de backup
cat > backup_portainer.sh << 'EOF'
#!/bin/bash
echo "🔍 Verificando Portainer existente..."

if docker ps -a | grep -q portainer; then
    echo "📦 Portainer encontrado, creando backup..."

    # Obtener ruta de datos de Portainer
    PORTAINER_DATA=$(docker inspect portainer 2>/dev/null | grep -A 10 "Mounts" | grep "Source" | cut -d'"' -f4 | head -1)

    if [ ! -z "$PORTAINER_DATA" ] && [ -d "$PORTAINER_DATA" ]; then
        # Backup de bind mount
        BACKUP_DIR="/tmp/portainer-backup-$(date +%Y%m%d-%H%M%S)"
        sudo cp -r "$PORTAINER_DATA" "$BACKUP_DIR"
        echo "✅ Backup creado en: $BACKUP_DIR"
        echo "📁 Para restaurar: sudo cp -r $BACKUP_DIR/* /mnt/sda1/portainer/data/"
    else
        # Backup de volumen Docker
        docker run --rm -v portainer_data:/data -v /tmp:/backup alpine tar czf /backup/portainer-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
        echo "✅ Backup de volumen creado en /tmp/"
    fi
else
    echo "ℹ️  No se encontró Portainer existente"
fi
EOF

chmod +x backup_portainer.sh
```

### 1. Clonar o transferir el proyecto

```bash
cd /mnt/sda1/shared/Projects/coach-motivacional-bot

# Si tienes los archivos localmente
scp -r coach-motivacional-bot/* david@<ip-raspberry>:/mnt/sda1/shared/Projects/coach-motivacional-bot/

# O crear los archivos directamente (ver archivos incluidos)
```

### 2. Configurar variables de entorno

```bash
# Crear archivo .env
nano .env
```

Contenido del archivo `.env`:

```env
# Tokens requeridos
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
GROQ_API_KEY=tu_api_key_de_groq_aqui

# Configuración opcional
TZ=Europe/Madrid
LOG_LEVEL=INFO
```

### 3. Construir y ejecutar con Docker Compose

```bash
# Construir la imagen
docker-compose build

# Ejecutar en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f coach-bot
```

## Gestión con Portainer

### 1. Acceder a Portainer

- Abrir navegador: `http://<ip-raspberry>:9000`
- Ir a **Containers** para ver el bot ejecutándose

### 2. Operaciones comunes en Portainer

**Ver logs del bot:**

1. Containers → `coach-motivacional-bot`
2. Click en **Logs**
3. Activar **Auto-refresh** para logs en tiempo real

**Reiniciar el bot:**

1. Containers → `coach-motivacional-bot`
2. Click en **Restart**

**Actualizar el bot:**

1. Containers → `coach-motivacional-bot`
2. Click en **Recreate**
3. Activar **Pull latest image**

**Ver métricas de recursos:**

1. Containers → `coach-motivacional-bot`
2. Click en **Stats**

### 3. Monitor web integrado

- Acceder a: `http://<ip-raspberry>:8080`
- Ver estado del bot, logs y métricas del sistema
- Interfaz web personalizada para monitoreo

## Comandos útiles de Docker

### Gestión básica

```bash
# Ver contenedores ejecutándose
docker ps

# Ver logs del bot
docker logs coach-motivacional-bot -f

# Entrar al contenedor (debugging)
docker exec -it coach-motivacional-bot /bin/bash

# Ver uso de recursos
docker stats coach-motivacional-bot

# Parar el bot
docker-compose down

# Reiniciar el bot
docker-compose restart coach-bot
```

### Mantenimiento

```bash
# Limpiar imágenes no usadas
docker image prune -f

# Ver espacio usado por Docker
docker system df

# Backup de volúmenes
docker run --rm -v coach-bot-data:/data -v /mnt/sda1/shared/Projects/coach-bot-backups:/backup alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restaurar backup
docker run --rm -v coach-bot-data:/data -v /mnt/sda1/shared/Projects/coach-bot-backups:/backup alpine tar xzf /backup/data-backup-YYYYMMDD.tar.gz -C /data
```

## Configuración avanzada

### 1. Límites de recursos para Raspberry Pi

El `docker-compose.yml` incluye límites optimizados:

- **Memoria máxima:** 512MB
- **CPU máximo:** 50% de un core
- **Logs rotativos:** Máximo 10MB por archivo

### 2. Volúmenes persistentes

Todos los datos se guardan en el disco externo:

- **Base de datos:** `/mnt/sda1/shared/Projects/coach-bot-data`
- **Logs:** `/mnt/sda1/shared/Projects/coach-bot-logs`
- **Backups:** `/mnt/sda1/shared/Projects/coach-bot-backups`

### 3. Healthcheck automático

Docker verifica cada 30 segundos que el bot esté funcionando:

- Reinicio automático si falla
- Notificaciones en Portainer

## Actualización del bot

### Método 1: Desde Portainer (recomendado)

1. Ir a **Images** en Portainer
2. Buscar la imagen del bot
3. Click en **Pull** para descargar nueva versión
4. Ir a **Containers** → bot → **Recreate**

### Método 2: Desde línea de comandos

```bash
cd /mnt/sda1/shared/Projects/coach-motivacional-bot

# Descargar cambios (si usas git)
git pull

# Reconstruir imagen
docker-compose build --no-cache

# Recrear contenedor
docker-compose up -d --force-recreate
```

## Monitoreo y alertas

### 1. Monitor web integrado

- **URL:** `http://<ip-raspberry>:8080`
- **Características:**
  - Estado del bot en tiempo real
  - Logs visuales
  - Métricas del sistema
  - Acceso directo a Portainer

### 2. Logs estructurados

```bash
# Ver logs por nivel
docker logs coach-motivacional-bot 2>&1 | grep ERROR
docker logs coach-motivacional-bot 2>&1 | grep WARNING

# Logs con timestamps
docker logs coach-motivacional-bot -t

# Últimas 100 líneas
docker logs coach-motivacional-bot --tail 100
```

### 3. Alertas automáticas (opcional)

Configurar notificaciones cuando el bot falle:

```bash
# Script de monitoreo
cat > /home/david/monitor-bot.sh << 'EOF'
#!/bin/bash
if ! docker ps | grep -q coach-motivacional-bot; then
    echo "Bot caído - $(date)" | mail -s "Alert: Coach Bot Down" tu@email.com
fi
EOF

# Añadir a cron cada 5 minutos
echo "*/5 * * * * /home/david/monitor-bot.sh" | crontab -
```

## Solución de problemas

### Bot no inicia

```bash
# Ver logs de error
docker logs coach-motivacional-bot

# Verificar variables de entorno
docker exec coach-motivacional-bot env | grep -E "(TELEGRAM|GROQ)"

# Verificar conectividad
docker exec coach-motivacional-bot ping -c 3 api.telegram.org
```

### Problemas de memoria

```bash
# Ver uso de memoria
docker stats --no-stream

# Reiniciar si usa mucha memoria
docker-compose restart coach-bot
```

### Problemas de disco

```bash
# Ver espacio disponible
df -h /mnt/sda1

# Limpiar logs antiguos
find /mnt/sda1/shared/Projects/coach-bot-logs -name "*.log" -mtime +7 -delete
```

## Backup y restauración

### Backup completo

```bash
#!/bin/bash
# Script de backup completo
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/mnt/sda1/shared/Projects/coach-bot-backups"

# Parar el bot temporalmente
docker-compose stop coach-bot

# Crear backup de datos
tar -czf "$BACKUP_DIR/complete-backup-$DATE.tar.gz" \
    /mnt/sda1/shared/Projects/coach-bot-data \
    /mnt/sda1/shared/Projects/coach-motivacional-bot/.env

# Reiniciar el bot
docker-compose start coach-bot

echo "Backup completo creado: complete-backup-$DATE.tar.gz"
```

### Restauración

```bash
# Parar el bot
docker-compose down

# Restaurar datos
tar -xzf complete-backup-YYYYMMDD_HHMMSS.tar.gz -C /

# Reiniciar
docker-compose up -d
```

¡Con Docker y Portainer tendrás una gestión profesional y súper fácil de tu bot de coaching! 🚀
