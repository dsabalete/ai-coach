#!/bin/sh

# Iniciar cron en background
crond -b

# Ejecutar recolección inicial de datos
/usr/local/bin/update-logs.sh
/usr/local/bin/get-system-info.sh

# Iniciar nginx en foreground
nginx -g "daemon off;"