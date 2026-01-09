#!/usr/bin/env python3
"""
Script para limpiar webhooks de Telegram y resolver conflictos
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN no encontrado en .env")
    exit(1)

def clear_webhook():
    """Eliminar webhook configurado"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    
    try:
        response = requests.post(url)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook eliminado correctamente")
        else:
            print(f"❌ Error eliminando webhook: {result.get('description')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def get_webhook_info():
    """Obtener información del webhook actual"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result.get('result', {})
            print("📋 Información del webhook:")
            print(f"   URL: {webhook_info.get('url', 'No configurado')}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error: {webhook_info.get('last_error_message', 'Ninguno')}")
        else:
            print(f"❌ Error obteniendo info: {result.get('description')}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def get_me():
    """Verificar que el token funciona"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"🤖 Bot: {bot_info.get('first_name')} (@{bot_info.get('username')})")
            return True
        else:
            print(f"❌ Token inválido: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Limpiando configuración de Telegram Bot...")
    
    # Verificar token
    if not get_me():
        exit(1)
    
    # Mostrar info actual
    get_webhook_info()
    
    # Limpiar webhook
    clear_webhook()
    
    print("\n✅ Limpieza completada. Ahora puedes reiniciar el bot.")