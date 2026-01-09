from groq import Groq
from typing import List, Dict
import json
from groq_models import get_model_for_task

class AICoach:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def generate_motivational_message(self, user_context: Dict) -> str:
        """Genera un mensaje motivacional personalizado"""
        
        system_prompt = """
        Eres un coach motivacional personal empático y profesional. Tu objetivo es:
        - Motivar y animar al usuario de forma genuina
        - Dar consejos prácticos y alcanzables
        - Adaptar tu tono al progreso y estado de ánimo del usuario
        - Ser conciso pero impactante (máximo 200 palabras)
        - Usar un lenguaje cercano y positivo en español
        """
        
        user_prompt = f"""
        Contexto del usuario:
        - Objetivos actuales: {user_context.get('goals', 'No definidos')}
        - Progreso reciente: {user_context.get('recent_progress', 'Sin datos')}
        - Estado de ánimo: {user_context.get('mood', 'Neutral')}
        - Situación actual: {user_context.get('current_situation', 'Check-in diario')}
        
        Genera un mensaje motivacional personalizado.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=get_model_for_task("motivational_message"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"¡Hola! Hoy es un gran día para dar un paso más hacia tus objetivos. ¿Cómo te sientes? 💪"
    
    def analyze_goal(self, goal_description: str) -> Dict:
        """Analiza un objetivo y sugiere mejoras"""
        
        system_prompt = """
        Eres un experto en establecimiento de objetivos. Analiza el objetivo del usuario y:
        1. Evalúa si es específico, medible, alcanzable, relevante y temporal (SMART)
        2. Sugiere mejoras si es necesario
        3. Propón pasos concretos para alcanzarlo
        4. Responde en formato JSON con: {"analysis": "...", "suggestions": ["...", "..."], "steps": ["...", "..."]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=get_model_for_task("goal_analysis"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Objetivo: {goal_description}"}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            return {
                "analysis": "Objetivo registrado correctamente",
                "suggestions": ["Mantén el enfoque en acciones específicas"],
                "steps": ["Define el primer paso pequeño", "Establece un horario regular"]
            }
    
    def generate_daily_question(self, goals: List[str]) -> str:
        """Genera una pregunta reflexiva diaria"""
        
        questions = [
            "¿Qué pequeño paso diste hoy hacia tus objetivos?",
            "¿Cómo te sientes con tu progreso actual?",
            "¿Qué obstáculo superaste hoy?",
            "¿Qué aprendiste sobre ti mismo/a hoy?",
            "¿Qué te motivó más durante el día?",
            "¿Cómo puedes mejorar mañana?",
            "¿Qué logro, por pequeño que sea, celebras hoy?"
        ]
        
        if goals:
            goal_specific = [
                f"¿Cómo avanzaste hoy en: {goals[0]}?",
                f"¿Qué te acercó más a conseguir: {goals[0]}?",
                f"¿Qué desafío encontraste trabajando en: {goals[0]}?"
            ]
            questions.extend(goal_specific)
        
        import random
        return random.choice(questions)