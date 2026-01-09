#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba específica del análisis de objetivos
"""

import os
from dotenv import load_dotenv
from ai_coach import AICoach

def test_goal_analysis():
    """Prueba el análisis de objetivos que puede estar causando el error 400"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No hay GROQ_API_KEY")
        return
    
    coach = AICoach(api_key)
    
    # Probar diferentes tipos de objetivos
    test_goals = [
        "Hacer ejercicio",
        "Quiero estar más en forma",
        "Leer 2 libros este mes",
        "Ahorrar dinero para vacaciones",
        "Mejorar en el trabajo"
    ]
    
    print("🧪 Probando análisis de objetivos...")
    print("=" * 50)
    
    for i, goal in enumerate(test_goals, 1):
        print(f"\n{i}. Objetivo: '{goal}'")
        
        try:
            result = coach.analyze_goal(goal)
            print(f"✅ Análisis exitoso:")
            print(f"   - Análisis: {result.get('analysis', 'N/A')[:100]}...")
            print(f"   - Sugerencias: {len(result.get('suggestions', []))} items")
            print(f"   - Pasos: {len(result.get('steps', []))} items")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_motivational_message():
    """Prueba los mensajes motivacionales"""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ No hay GROQ_API_KEY")
        return
    
    coach = AICoach(api_key)
    
    print("\n🧪 Probando mensajes motivacionales...")
    print("=" * 50)
    
    test_contexts = [
        {
            'goals': ['Hacer ejercicio'],
            'recent_progress': 'Hoy caminé 30 minutos',
            'mood': 4,
            'current_situation': 'Check-in diario'
        },
        {
            'goals': ['Leer más', 'Estudiar programación'],
            'recent_progress': 'Leí 20 páginas de un libro técnico',
            'mood': 3,
            'current_situation': 'Progreso semanal'
        }
    ]
    
    for i, context in enumerate(test_contexts, 1):
        print(f"\n{i}. Contexto: {context['goals']}")
        
        try:
            message = coach.generate_motivational_message(context)
            print(f"✅ Mensaje generado:")
            print(f"   {message[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_goal_analysis()
    test_motivational_message()