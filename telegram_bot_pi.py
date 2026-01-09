#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram para Coach Motivacional Personal - Versión Raspberry Pi
Optimizado para menor uso de recursos
"""

import os
import logging
import gc
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

from database import Database
from ai_coach import AICoach

# Cargar variables de entorno
load_dotenv()

# Configurar logging optimizado para Pi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,  # Menos verbose para ahorrar recursos
    handlers=[
        logging.FileHandler('/tmp/coach_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Estados de conversación
WAITING_GOAL, WAITING_PROGRESS, WAITING_MOOD = range(3)

class MotivationalBotPi:
    def __init__(self):
        self.db = Database()
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            self.ai_coach = AICoach(groq_key)
        else:
            self.ai_coach = None
            logger.error("GROQ_API_KEY no encontrada")
        
        # Cache para reducir llamadas a la IA
        self.message_cache = {}
        self.cache_size = 50  # Limitar tamaño del cache
    
    def _get_cached_or_generate(self, cache_key, generator_func, *args):
        """Obtiene mensaje del cache o lo genera"""
        if cache_key in self.message_cache:
            return self.message_cache[cache_key]
        
        result = generator_func(*args)
        
        # Mantener cache limitado
        if len(self.message_cache) >= self.cache_size:
            # Eliminar el más antiguo
            oldest_key = next(iter(self.message_cache))
            del self.message_cache[oldest_key]
        
        self.message_cache[cache_key] = result
        return result
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Bienvenida optimizada"""
        user = update.effective_user
        
        # Registrar usuario en la base de datos
        self.db.add_user(user.id, user.username, user.first_name)
        
        welcome_message = f"""¡Hola {user.first_name}! 👋

Soy tu coach motivacional personal ejecutándose en Raspberry Pi.

Comandos:
/objetivo - Nuevo objetivo
/progreso - Registrar progreso
/estado - Ver objetivos
/motivacion - Mensaje motivacional
/ayuda - Ayuda completa

¿Listo para empezar?"""
        
        # Teclado simplificado para ahorrar memoria
        keyboard = [
            [KeyboardButton("🎯 Objetivo"), KeyboardButton("📊 Progreso")],
            [KeyboardButton("💪 Motivación"), KeyboardButton("❓ Ayuda")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        
        # Limpiar memoria
        gc.collect()
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ayuda simplificado"""
        help_text = """🤖 Coach Motivacional (Raspberry Pi)

/start - Iniciar
/objetivo - Nuevo objetivo
/progreso - Registrar progreso diario
/estado - Ver objetivos y progreso
/motivacion - Mensaje motivacional
/ayuda - Esta ayuda

Botones rápidos disponibles en el teclado.
¡Estoy aquí 24/7 para apoyarte! 🚀"""
        
        await update.message.reply_text(help_text)
    
    async def add_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar proceso de añadir objetivo"""
        await update.message.reply_text(
            "🎯 Describe tu objetivo de forma específica:\n\n"
            "Ejemplos:\n"
            "• 'Ejercicio 30 min, 4 veces/semana'\n"
            "• 'Leer 2 libros este mes'\n"
            "• 'Ahorrar €500 en 3 meses'"
        )
        return WAITING_GOAL
    
    async def process_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar objetivo con análisis optimizado"""
        user_id = update.effective_user.id
        goal_text = update.message.text
        
        # Guardar en base de datos primero
        goal_id = self.db.add_goal(user_id, goal_text, "", "personal")
        
        # Análisis con IA (con cache)
        if self.ai_coach:
            try:
                cache_key = f"goal_analysis_{hash(goal_text)}"
                analysis = self._get_cached_or_generate(
                    cache_key, 
                    self.ai_coach.analyze_goal, 
                    goal_text
                )
                
                response = f"✅ **Objetivo registrado!**\n\n🎯 {goal_text}\n\n"
                response += f"📋 **Análisis:** {analysis.get('analysis', 'Objetivo bien definido')[:150]}...\n\n"
                response += "💡 **Sugerencias:**\n"
                
                for suggestion in analysis.get('suggestions', [])[:2]:  # Limitar a 2
                    response += f"• {suggestion}\n"
                
                response += "\n🚀 **Primeros pasos:**\n"
                for step in analysis.get('steps', [])[:2]:  # Limitar a 2
                    response += f"• {step}\n"
                
            except Exception as e:
                logger.error(f"Error en análisis IA: {e}")
                response = f"✅ **Objetivo registrado!**\n\n🎯 {goal_text}\n\n"
                response += "¡Excelente! Usa /progreso para registrar tu avance diario."
        else:
            response = f"✅ **Objetivo registrado!**\n\n🎯 {goal_text}\n\n"
            response += "¡Perfecto! Usa /progreso para tu seguimiento diario."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Limpiar memoria
        gc.collect()
        return ConversationHandler.END
    
    async def check_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check-in de progreso simplificado"""
        user_id = update.effective_user.id
        goals = self.db.get_user_goals(user_id)
        
        if not goals:
            await update.message.reply_text(
                "🤔 No tienes objetivos definidos.\nUsa /objetivo para crear uno."
            )
            return ConversationHandler.END
        
        # Mostrar objetivos (limitado para ahorrar memoria)
        goals_text = "📋 **Tus objetivos:**\n\n"
        for i, goal in enumerate(goals[:3], 1):  # Máximo 3
            goals_text += f"{i}. {goal[1][:50]}...\n"
        
        goals_text += "\n💭 ¿Cómo fue tu progreso hoy?"
        
        await update.message.reply_text(goals_text, parse_mode='Markdown')
        return WAITING_PROGRESS
    
    async def process_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar progreso"""
        progress_text = update.message.text[:200]  # Limitar longitud
        
        await update.message.reply_text(
            "😊 Estado de ánimo (1-5):\n"
            "1️⃣ Muy bajo  2️⃣ Bajo  3️⃣ Regular\n"
            "4️⃣ Bueno  5️⃣ Excelente"
        )
        
        context.user_data['progress_text'] = progress_text
        return WAITING_MOOD
    
    async def process_mood(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar estado de ánimo y generar respuesta"""
        user_id = update.effective_user.id
        mood_text = update.message.text
        
        try:
            mood_score = int(mood_text)
            if mood_score < 1 or mood_score > 5:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Por favor, envía un número del 1 al 5.")
            return WAITING_MOOD
        
        # Registrar en base de datos
        progress_text = context.user_data.get('progress_text', '')
        goals = self.db.get_user_goals(user_id)
        
        if goals:
            self.db.add_daily_progress(user_id, goals[0][0], progress_text, mood_score)
        
        # Respuesta motivacional optimizada
        if self.ai_coach and mood_score >= 3:  # Solo usar IA si el ánimo es bueno
            try:
                user_context = {
                    'goals': [goal[1][:50] for goal in goals[:2]],  # Limitar datos
                    'recent_progress': progress_text,
                    'mood': mood_score,
                    'current_situation': 'Check-in diario'
                }
                
                cache_key = f"motivation_{user_id}_{mood_score}_{hash(progress_text[:50])}"
                message = self._get_cached_or_generate(
                    cache_key,
                    self.ai_coach.generate_motivational_message,
                    user_context
                )
            except Exception as e:
                logger.error(f"Error generando motivación: {e}")
                message = "¡Excelente progreso! Sigue así, cada paso cuenta. 💪"
        else:
            # Mensajes predefinidos para ahorrar recursos
            messages = {
                1: "Entiendo que hoy fue difícil. Mañana es una nueva oportunidad. 🌅",
                2: "Los días difíciles también cuentan. Estás siendo valiente. 💙",
                3: "Un día regular es progreso. Mantén el rumbo. ⚡",
                4: "¡Buen trabajo hoy! Tu constancia está dando frutos. 🌟",
                5: "¡Increíble! Días como hoy te acercan a tus sueños. 🚀"
            }
            message = messages.get(mood_score, "¡Sigue adelante! 💪")
        
        mood_emoji = ["😔", "😐", "🙂", "😊", "🤩"][mood_score - 1]
        response = f"✅ **Registrado!** {mood_emoji}\n\n{message}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Limpiar memoria y contexto
        context.user_data.clear()
        gc.collect()
        return ConversationHandler.END
    
    async def show_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Estado simplificado"""
        user_id = update.effective_user.id
        goals = self.db.get_user_goals(user_id)
        recent_progress = self.db.get_user_progress(user_id, 3)  # Solo últimos 3
        
        if not goals:
            await update.message.reply_text("🤔 Sin objetivos. Usa /objetivo para crear uno.")
            return
        
        status_text = "📊 **Estado Actual**\n\n🎯 **Objetivos:**\n"
        for i, goal in enumerate(goals[:2], 1):  # Máximo 2
            status_text += f"{i}. {goal[1][:40]}...\n"
        
        if recent_progress:
            status_text += "\n📈 **Progreso reciente:**\n"
            for progress in recent_progress[:2]:  # Máximo 2
                mood = "😔😐🙂😊🤩"[progress[1] - 1] if progress[1] else "😐"
                status_text += f"• {progress[2]}: {mood}\n"
        
        status_text += "\n💪 ¡Sigue así!"
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def get_motivation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Motivación rápida"""
        messages = [
            "¡Hoy es un gran día para avanzar! 🌟",
            "Cada pequeño paso cuenta. ¡Sigue así! 💪",
            "Tu futuro yo te agradecerá el esfuerzo de hoy. 🚀",
            "Los sueños se construyen día a día. ¡Adelante! ⭐",
            "Eres más fuerte de lo que crees. 💙"
        ]
        
        import random
        message = random.choice(messages)
        await update.message.reply_text(f"💪 {message}")
    
    async def handle_quick_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Botones rápidos optimizados"""
        text = update.message.text
        
        if text == "🎯 Objetivo":
            return await self.add_goal(update, context)
        elif text == "📊 Progreso":
            return await self.check_progress(update, context)
        elif text == "💪 Motivación":
            await self.get_motivation(update, context)
        elif text == "❓ Ayuda":
            await self.help_command(update, context)
        else:
            await update.message.reply_text("🤔 Usa los botones del menú o /ayuda")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancelar conversación"""
        context.user_data.clear()
        await update.message.reply_text("❌ Cancelado. Usa /ayuda para ver comandos.")
        return ConversationHandler.END

def main():
    """Función principal optimizada para Pi"""
    
    # Verificar variables de entorno
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado")
        return
    
    if not groq_key:
        print("⚠️  GROQ_API_KEY no encontrado - IA limitada")
    
    # Crear bot
    bot = MotivationalBotPi()
    
    # Configuración optimizada para Pi
    application = Application.builder().token(bot_token).build()
    
    # Manejadores de conversación
    goal_handler = ConversationHandler(
        entry_points=[CommandHandler('objetivo', bot.add_goal)],
        states={
            WAITING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.process_goal)],
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)],
    )
    
    progress_handler = ConversationHandler(
        entry_points=[CommandHandler('progreso', bot.check_progress)],
        states={
            WAITING_PROGRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.process_progress)],
            WAITING_MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.process_mood)],
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)],
    )
    
    # Registrar manejadores
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("ayuda", bot.help_command))
    application.add_handler(CommandHandler("estado", bot.show_status))
    application.add_handler(CommandHandler("motivacion", bot.get_motivation))
    application.add_handler(goal_handler)
    application.add_handler(progress_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_quick_buttons))
    
    # Iniciar con configuración optimizada
    print("🍓 Coach Motivacional Pi iniciado...")
    print("Optimizado para Raspberry Pi - Uso eficiente de recursos")
    print("Presiona Ctrl+C para detener")
    
    # Configuración de polling optimizada
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=2.0,  # Menos frecuente para ahorrar recursos
        timeout=20,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30
    )

if __name__ == '__main__':
    main()