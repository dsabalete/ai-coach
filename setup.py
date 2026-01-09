#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración inicial para el Coach Motivacional Bot
"""

import os
import sys

def create_env_file():
    """Crear archivo .env si no existe"""
    if not os.path.exists('.env'):
        print("📝 Creando archivo .env...")
        
        telegram_token = input("🤖 Ingresa tu TELEGRAM_BOT_TOKEN: ").strip()
        groq_key = input("🧠 Ingresa tu GROQ_API_KEY: ").strip()
        
        with open('.env', 'w') as f:
            f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")
            f.write(f"GROQ_API_KEY={groq_key}\n")
        
        print("✅ Archivo .env creado exitosamente!")
    else:
        print("ℹ️  El archivo .env ya existe.")

def install_dependencies():
    """Instalar dependencias de Python"""
    print("📦 Instalando dependencias...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✅ Dependencias instaladas!")

def test_database():
    """Probar la conexión a la base de datos"""
    print("🗄️  Probando base de datos...")
    try:
        from database import Database
        db = Database()
        print("✅ Base de datos inicializada correctamente!")
    except Exception as e:
        print(f"❌ Error con la base de datos: {e}")

def main():
    """Función principal de configuración"""
    print("🚀 Configuración inicial del Coach Motivacional Bot")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Instalar dependencias
    install_dependencies()
    
    # Crear archivo .env
    create_env_file()
    
    # Probar base de datos
    test_database()
    
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Verifica que tu archivo .env tenga los tokens correctos")
    print("2. Ejecuta: python telegram_bot.py")
    print("3. Busca tu bot en Telegram y envía /start")
    print("\n💡 Consejos:")
    print("- Obtén tu bot token de @BotFather en Telegram")
    print("- Consigue tu API key en https://console.groq.com/keys")
    print("- Mantén tus tokens seguros y privados")

if __name__ == "__main__":
    main()