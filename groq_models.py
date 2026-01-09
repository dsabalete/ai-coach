"""
Configuración de modelos disponibles en Groq
Actualizado para enero 2025
"""

# Modelos disponibles en Groq (gratuitos)
GROQ_MODELS = {
    # Modelos Llama más potentes
    "llama-3.1-70b-versatile": {
        "description": "Modelo más potente, ideal para coaching complejo",
        "use_case": "Mensajes motivacionales detallados",
        "speed": "medio",
        "quality": "alta"
    },
    
    "llama-3.1-8b-instant": {
        "description": "Modelo rápido, ideal para respuestas inmediatas", 
        "use_case": "Análisis de objetivos, respuestas rápidas",
        "speed": "muy rápido",
        "quality": "buena"
    },
    
    # Modelos Mixtral
    "mixtral-8x7b-32768": {
        "description": "Buen balance entre velocidad y calidad",
        "use_case": "Uso general, conversaciones",
        "speed": "rápido", 
        "quality": "muy buena"
    },
    
    # Modelos Gemma
    "gemma2-9b-it": {
        "description": "Modelo eficiente de Google",
        "use_case": "Tareas específicas, análisis",
        "speed": "rápido",
        "quality": "buena"
    }
}

# Configuración recomendada por tipo de tarea
TASK_MODEL_MAPPING = {
    "motivational_message": "llama-3.1-70b-versatile",  # Calidad alta para motivación
    "goal_analysis": "llama-3.1-8b-instant",           # Velocidad para análisis
    "daily_question": "mixtral-8x7b-32768",            # Balance para preguntas
    "quick_response": "llama-3.1-8b-instant"           # Velocidad para respuestas rápidas
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