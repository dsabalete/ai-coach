#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la integración con Groq
"""

import os
from dotenv import load_dotenv
from ai_coach import AICoach
from groq_models import GROQ_MODELS, get_model_for_task

def test_groq_connection():
    """Prueba la conexión básica con Groq"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY no encontrada en .env")
        return False
    
    try:
        coach = AICoach(api_key)
        
        # Prueba simple
        test_context = {
            'goals': ['Hacer ejercicio 3 veces por semana'],
            'recent_progress': 'Hoy hice 30 minutos de cardio',
            'mood': 4,
            'current_situation': 'Prueba de conexión'
        }
        
        print("🧪 Probando generación de mensaje motivacional...")
        message = coach.generate_motivational_message(test_context)
        print(f"✅ Respuesta recibida: {message[:100]}...")
        
        print("\n🧪 Probando análisis de objetivo...")
        analysis = coach.analyze_goal("Quiero estar más en forma")
        print(f"✅ Análisis recibido: {analysis.get('analysis', 'Sin análisis')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar con Groq: {e}")
        return False

def show_available_models():
    """Muestra los modelos disponibles"""
    print("\n📋 Modelos disponibles en Groq:")
    print("=" * 50)
    
    for model_name, info in GROQ_MODELS.items():
        print(f"\n🤖 {model_name}")
        print(f"   📝 {info['description']}")
        print(f"   🎯 Uso: {info['use_case']}")
        print(f"   ⚡ Velocidad: {info['speed']}")
        print(f"   ⭐ Calidad: {info['quality']}")
    
    print("\n🔧 Configuración de tareas:")
    print("- Mensajes motivacionales:", get_model_for_task("motivational_message"))
    print("- Análisis de objetivos:", get_model_for_task("goal_analysis"))
    print("- Preguntas diarias:", get_model_for_task("daily_question"))

def main():
    """Función principal de prueba"""
    print("🚀 Prueba de integración con Groq")
    print("=" * 40)
    
    # Mostrar modelos disponibles
    show_available_models()
    
    # Probar conexión
    print("\n🔌 Probando conexión con Groq...")
    if test_groq_connection():
        print("\n🎉 ¡Integración con Groq funcionando correctamente!")
        print("\n💡 El bot está listo para usar. Ejecuta:")
        print("   python telegram_bot.py")
    else:
        print("\n❌ Hay problemas con la configuración.")
        print("\n🔧 Verifica:")
        print("1. Que tengas un archivo .env con GROQ_API_KEY")
        print("2. Que la API key sea válida")
        print("3. Que tengas conexión a internet")

if __name__ == "__main__":
    main()