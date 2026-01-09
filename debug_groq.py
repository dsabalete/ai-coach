#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para problemas con Groq API
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json

def test_groq_api():
    """Prueba detallada de la API de Groq"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    
    print("🔍 Diagnóstico de Groq API")
    print("=" * 40)
    
    # Verificar API key
    if not api_key:
        print("❌ GROQ_API_KEY no encontrada en .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    
    # Crear cliente
    try:
        client = Groq(api_key=api_key)
        print("✅ Cliente Groq creado correctamente")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return False
    
    # Probar modelos disponibles
    print("\n🤖 Probando modelos...")
    
    models_to_test = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile", 
        "mixtral-8x7b-32768"
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Probando modelo: {model}")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un asistente útil."},
                    {"role": "user", "content": "Hola, ¿cómo estás?"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            print(f"✅ {model}: {response.choices[0].message.content[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ {model}: {str(e)}")
            
            # Mostrar detalles del error
            if hasattr(e, 'response'):
                print(f"   Status: {e.response.status_code}")
                print(f"   Response: {e.response.text}")
    
    return False

def test_simple_request():
    """Prueba con la petición más simple posible"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No hay API key para probar")
        return
    
    print("\n🔬 Prueba con petición mínima...")
    
    try:
        client = Groq(api_key=api_key)
        
        # Petición ultra simple
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        print("✅ Petición simple exitosa!")
        print(f"Respuesta: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error en petición simple: {e}")
        
        # Información detallada del error
        print(f"Tipo de error: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'response'):
            print(f"Response text: {e.response.text}")

def check_api_key_format():
    """Verifica el formato de la API key"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No hay API key para verificar")
        return
    
    print(f"\n🔑 Verificando formato de API key...")
    print(f"Longitud: {len(api_key)}")
    print(f"Prefijo: {api_key[:10]}...")
    print(f"Contiene espacios: {'Sí' if ' ' in api_key else 'No'}")
    print(f"Contiene saltos de línea: {'Sí' if chr(10) in api_key else 'No'}")
    
    # Las API keys de Groq suelen empezar con 'gsk_'
    if api_key.startswith('gsk_'):
        print("✅ Formato de API key parece correcto (empieza con gsk_)")
    else:
        print("⚠️  API key no empieza con 'gsk_' - verifica que sea correcta")

def main():
    """Función principal de diagnóstico"""
    print("🚀 Diagnóstico completo de Groq")
    print("=" * 50)
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env no encontrado")
        print("Crea un archivo .env con tu GROQ_API_KEY")
        return
    
    # Verificar formato de API key
    check_api_key_format()
    
    # Probar petición simple
    test_simple_request()
    
    # Probar API completa
    if test_groq_api():
        print("\n🎉 ¡Groq API funcionando correctamente!")
    else:
        print("\n❌ Hay problemas con Groq API")
        print("\n🔧 Posibles soluciones:")
        print("1. Verifica que tu API key sea válida")
        print("2. Asegúrate de que no tenga espacios extra")
        print("3. Verifica tu conexión a internet")
        print("4. Comprueba que tu cuenta de Groq esté activa")

if __name__ == "__main__":
    main()