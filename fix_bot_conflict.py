#!/usr/bin/env python3
"""
Script para resolver conflictos de múltiples instancias del bot
"""

import os
import requests
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def clear_pending_updates():
    """Limpiar actualizaciones pendientes usando offset alto"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        # Obtener actualizaciones pendientes
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            updates = result.get('result', [])
            if updates:
                # Usar offset alto para marcar todas como procesadas
                last_update_id = max(update['update_id'] for update in updates)
                clear_url = f"{url}?offset={last_update_id + 1}&timeout=1"
                requests.get(clear_url)
                print(f"✅ Limpiadas {len(updates)} actualizaciones pendientes")
            else:
                print("✅ No hay actualizaciones pendientes")
        else:
            print(f"❌ Error: {result.get('description')}")
            
    except Exception as e:
        print(f"❌ Error limpiando actualizaciones: {e}")

def force_clear_session():
    """Forzar limpieza de sesión usando timeout largo"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        print("🔄 Forzando limpieza de sesión...")
        # Hacer una llamada con timeout largo para forzar desconexión
        params = {
            'offset': -1,
            'timeout': 1,
            'limit': 1
        }
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Sesión limpiada")
        else:
            print(f"⚠️  Respuesta: {result.get('description')}")
            
    except requests.exceptions.Timeout:
        print("✅ Timeout esperado - sesión forzada a cerrar")
    except Exception as e:
        print(f"⚠️  Error (puede ser normal): {e}")

def wait_and_test():
    """Esperar y probar conexión"""
    print("⏳ Esperando 10 segundos para que se libere la conexión...")
    time.sleep(10)
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"✅ Bot disponible: {bot_info.get('first_name')} (@{bot_info.get('username')})")
            return True
        else:
            print(f"❌ Error: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Resolviendo conflicto de múltiples instancias del bot...")
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado")
        exit(1)
    
    # Paso 1: Limpiar actualizaciones pendientes
    clear_pending_updates()
    
    # Paso 2: Forzar limpieza de sesión
    force_clear_session()
    
    # Paso 3: Esperar y verificar
    if wait_and_test():
        print("\n✅ Conflicto resuelto. El bot debería funcionar ahora.")
        print("💡 Reinicia el contenedor del bot: docker-compose restart coach-bot")
    else:
        print("\n❌ El conflicto persiste. Verifica si hay otras instancias ejecutándose.")
        print("💡 Comandos útiles:")
        print("   - ps aux | grep telegram")
        print("   - docker ps -a | grep bot")
        print("   - pkill -f telegram_bot")