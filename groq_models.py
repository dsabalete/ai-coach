#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de modelos disponibles en Groq
Actualizado para enero 2025
"""

# Modelos disponibles en Groq (actualizados enero 2025)
GROQ_MODELS = {
    # Modelos Llama actuales
    "llama-3.1-8b-instant": {
        "description": "Modelo rápido y eficiente, ideal para respuestas inmediatas", 
        "use_case": "Análisis de objetivos, respuestas rápidas",
        "speed": "muy rápido (560 T/sec)",
        "quality": "buena"
    },
    
    "llama-3.3-70b-versatile": {
        "description": "Modelo más potente, ideal para coaching complejo",
        "use_case": "Mensajes motivacionales detallados",
        "speed": "rápido (280 T/sec)",
        "quality": "muy alta"
    },
    
    # Modelos Llama 4 (Preview)
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "description": "Llama 4 Scout - Modelo general potente",
        "use_case": "Uso general, razonamiento",
        "speed": "muy rápido (750 T/sec)",
        "quality": "alta"
    },
    
    "meta-llama/llama-4-maverick-17b-128e-instruct": {
        "description": "Llama 4 Maverick - Optimizado para multilingüe",
        "use_case": "Asistentes, chat, aplicaciones creativas",
        "speed": "rápido (600 T/sec)",
        "quality": "muy alta"
    },
    
    # Modelos GPT OSS
    "openai/gpt-oss-20b": {
        "description": "Modelo GPT open source 20B",
        "use_case": "Uso general, conversaciones",
        "speed": "muy rápido (1000 T/sec)",
        "quality": "buena"
    }
}

# Configuración recomendada por tipo de tarea (modelos actualizados)
TASK_MODEL_MAPPING = {
    "motivational_message": "llama-3.3-70b-versatile",     # Calidad alta para motivación
    "goal_analysis": "llama-3.1-8b-instant",               # Velocidad para análisis
    "daily_question": "llama-3.1-8b-instant",              # Velocidad para preguntas
    "quick_response": "llama-3.1-8b-instant"               # Velocidad para respuestas rápidas
}

def get_model_for_task(task_type: str) -> str:
    """Obtiene el modelo recomendado para un tipo de tarea"""
    return TASK_MODEL_MAPPING.get(task_type, "llama-3.1-8b-instant")

def get_model_info(model_name: str) -> dict:
    """Obtiene información sobre un modelo específico"""
    return GROQ_MODELS.get(model_name, {
        "description": "Modelo no encontrado",
        "use_case": "Desconocido",
        "speed": "desconocido",
        "quality": "desconocida"
    })