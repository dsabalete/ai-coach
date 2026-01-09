#!/bin/bash
# Script para obtener logs reales del contenedor

# Obtener logs del contenedor coach-motivacional-bot
docker logs coach-motivacional-bot --tail=500 --timestamps 2>/dev/null || echo "Error: No se pueden obtener los logs del contenedor"