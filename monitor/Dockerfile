FROM nginx:alpine

# Instalar Docker CLI y herramientas del sistema
RUN apk add --no-cache docker-cli procps

# Copiar scripts
COPY update-logs.sh /usr/local/bin/
COPY get-system-info.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/update-logs.sh /usr/local/bin/get-system-info.sh

# Crear cron jobs
RUN echo "*/1 * * * * /usr/local/bin/update-logs.sh" > /etc/crontabs/root
RUN echo "*/1 * * * * /usr/local/bin/get-system-info.sh" >> /etc/crontabs/root

# Script de inicio que ejecuta nginx y cron
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]