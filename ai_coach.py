#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración con Groq AI para coaching motivacional
"""

from groq import Groq
from typing import List, Dict
import json
from groq_models import get_model_for_task

class AICoach:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def generate_motivational_message(self, user_context: Dict) -> str:
        """Genera un mensaje motivacional personalizado"""
        
        # Validar y limpiar entrada
        goals = user_context.get('goals', [])
        if isinstance(goals, list):
            goals_text = ', '.join(str(g)[:100] for g in goals[:3])  # Limitar longitud
        else:
            goals_text = str(goals)[:100]
        
        recent_progress = str(user_context.get('recent_progress', 'Sin datos'))[:200]
        mood = user_context.get('mood', 'Neutral')
        situation = str(user_context.get('current_situation', 'Check-in diario'))[:100]
        
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
        - Objetivos actuales: {goals_text}
        - Progreso reciente: {recent_progress}
        - Estado de ánimo: {mood}
        - Situación actual: {situation}
        
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
            print(f"❌ Error en generate_motivational_message: {e}")
            return f"¡Hola! Hoy es un gran día para dar un paso más hacia tus objetivos. ¿Cómo te sientes? 💪"
    
    def analyze_goal(self, goal_description: str) -> Dict:
        """Analiza un objetivo y sugiere mejoras"""
        
        system_prompt = """
        Eres un experto en establecimiento de objetivos. Analiza el objetivo del usuario y responde SOLO con un JSON válido en este formato exacto:
        {
            "analysis": "Tu análisis del objetivo aquí",
            "suggestions": ["Sugerencia 1", "Sugerencia 2"],
            "steps": ["Paso 1", "Paso 2", "Paso 3"]
        }
        
        No añadas texto extra fuera del JSON. Solo responde con el JSON válido.
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
            
            response_text = response.choices[0].message.content.strip()
            print(f"🔍 Respuesta de IA para análisis: {response_text[:100]}...")
            
            # Intentar parsear JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as json_error:
                print(f"❌ Error parseando JSON: {json_error}")
                print(f"Respuesta completa: {response_text}")
                # Fallback con datos por defecto
                return {
                    "analysis": "Objetivo registrado correctamente",
                    "suggestions": ["Mantén el enfoque en acciones específicas"],
                    "steps": ["Define el primer paso pequeño", "Establece un horario regular"]
                }
        
        except Exception as e:
            print(f"❌ Error en analyze_goal: {e}")
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