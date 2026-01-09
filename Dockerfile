# Dockerfile para Coach Motivacional Bot - Optimizado para Raspberry Pi
FROM python:3.11-slim-bullseye

# Metadatos
LABEL maintainer="Coach Motivacional Bot"
LABEL description="Bot de Telegram para coaching motivacional personal"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Copiar y configurar entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs /app/backups \
    && chown -R botuser:botuser /app

# Cambiar a usuario no-root
USER botuser

# Exponer puerto para healthcheck (opcional)
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sqlite3; sqlite3.connect('/app/data/coach_bot.db').close()" || exit 1

# Comando por defecto
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python3", "telegram_bot_pi.py"]