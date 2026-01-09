# 🚨 Guía de Recuperación Docker - Problemas Comunes

## Problema: Script eliminó contenedores existentes

### Síntomas

- `docker ps -a` solo muestra Portainer o está vacío
- Perdiste servicios que tenías ejecutándose
- Portainer muestra configuración nueva/vacía

### Solución paso a paso

#### 1. Verificar estado actual

```bash
# Ver qué queda
docker ps -a
docker volume ls
docker images

# Buscar backups automáticos
ls -la /tmp/portainer-backup-*
ls -la /tmp/backup-*
```

#### 2. Restaurar Portainer si tienes backup

```bash
# Si tienes backup en /tmp/
BACKUP_DIR=$(ls -d /tmp/portainer-backup-* | head -1)

# Parar Portainer actual
docker stop portainer
docker rm portainer

# Restaurar datos
sudo mkdir -p /mnt/sda1/portainer/data
sudo cp -r $BACKUP_DIR/* /mnt/sda1/portainer/data/
sudo chown -R david:david /mnt/sda1/portainer/

# Recrear Portainer con datos originales
docker run -d \
  -p 8000:8000 \
  -p 9000:9000 \
  --name=portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /mnt/sda1/portainer/data:/data \
  portainer/portainer-ce:latest
```

#### 3. Recuperar servicios comunes

##### Grafana + Prometheus

```bash
# Crear red de monitoreo
docker network create monitor-net

# Prometheus
docker run -d \
  --name prometheus \
  --network monitor-net \
  -p 9090:9090 \
  -v prometheus-data:/prometheus \
  prom/prometheus:latest

# Grafana
docker run -d \
  --name grafana \
  --network monitor-net \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana:latest
```

##### Node Exporter

```bash
docker run -d \
  --name node-exporter \
  --network monitor-net \
  -p 9100:9100 \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  -v /:/rootfs:ro \
  prom/node-exporter:latest \
  --path.procfs=/host/proc \
  --path.rootfs=/rootfs \
  --path.sysfs=/host/sys \
  --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)($$|/)'
```

##### InfluxDB

```bash
docker run -d \
  --name influxdb \
  -p 8086:8086 \
  -v influxdb-data:/var/lib/influxdb2 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword \
  -e DOCKER_INFLUXDB_INIT_ORG=myorg \
  -e DOCKER_INFLUXDB_INIT_BUCKET=mybucket \
  influxdb:latest
```

##### Home Assistant

```bash
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Europe/Madrid \
  -v homeassistant-config:/config \
  -v /run/dbus:/run/dbus:ro \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

#### 4. Usar Portainer para recuperar más servicios

1. **Accede a Portainer:** `http://<ip-raspberry>:9000`
2. **App Templates:** Instala servicios comunes con un clic
3. **Stacks:** Recrea configuraciones docker-compose
4. **Volumes:** Verifica si hay datos recuperables

## Prevención futura

### Script de backup automático

```bash
#!/bin/bash
# backup_docker.sh - Ejecutar ANTES de cualquier instalación

echo "🔄 Creando backup completo de Docker..."

BACKUP_DIR="/mnt/sda1/backups/docker-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup de contenedores
docker ps -a --format "{{.Names}}\t{{.Image}}\t{{.Command}}\t{{.Ports}}" > "$BACKUP_DIR/containers.txt"

# Backup de volúmenes
docker volume ls > "$BACKUP_DIR/volumes.txt"

# Backup de redes
docker network ls > "$BACKUP_DIR/networks.txt"

# Backup de Portainer si existe
if docker ps -a | grep -q portainer; then
    PORTAINER_DATA=$(docker inspect portainer | grep -A 10 "Mounts" | grep "Source" | cut -d'"' -f4 | head -1)
    if [ ! -z "$PORTAINER_DATA" ]; then
        sudo cp -r "$PORTAINER_DATA" "$BACKUP_DIR/portainer-data"
    fi
fi

# Backup de docker-compose files
find /home/david -name "docker-compose.yml" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null
find /mnt/sda1 -name "docker-compose.yml" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null

echo "✅ Backup completo en: $BACKUP_DIR"
```

### Verificación pre-instalación

```bash
#!/bin/bash
# check_docker.sh - Ejecutar ANTES de scripts de instalación

echo "🔍 Verificando estado de Docker..."

echo "📦 Contenedores:"
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

echo -e "\n💾 Volúmenes:"
docker volume ls

echo -e "\n🌐 Redes:"
docker network ls

echo -e "\n⚠️  ADVERTENCIA:"
echo "Si continúas con la instalación, algunos de estos elementos podrían verse afectados."
echo "¿Has hecho backup? (Ejecuta backup_docker.sh primero)"
```

## Contacto de emergencia

Si nada de esto funciona:

1. **Parar todo Docker:**

```bash
docker stop $(docker ps -aq)
docker system prune -a --volumes
sudo systemctl restart docker
```

2. **Reinstalar Portainer limpio:**

```bash
docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v /mnt/sda1/portainer/data:/data portainer/portainer-ce:latest
```

3. **Usar Portainer para recrear todo desde cero**

## Lecciones aprendidas

- ✅ **SIEMPRE hacer backup antes de ejecutar scripts**
- ✅ **Verificar qué contenedores tienes ejecutándose**
- ✅ **Leer scripts antes de ejecutarlos**
- ✅ **Usar Portainer para gestión visual**
- ✅ **Mantener configuraciones docker-compose en git**
