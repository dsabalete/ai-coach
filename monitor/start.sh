#!/bin/sh

# Iniciar cron en background
crond -b

# Ejecutar actualización inicial de logs
/usr/local/bin/update-logs.sh

# Iniciar nginx en foreground
nginx -g "daemon off;"