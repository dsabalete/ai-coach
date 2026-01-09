FROM nginx:alpine

# Instalar Docker CLI
RUN apk add --no-cache docker-cli

# Copiar script de actualización de logs
COPY update-logs.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/update-logs.sh

# Crear cron job para actualizar logs cada 30 segundos
RUN echo "*/1 * * * * /usr/local/bin/update-logs.sh" > /etc/crontabs/root

# Script de inicio que ejecuta nginx y cron
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]