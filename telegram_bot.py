import os
import logging
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

from database import Database
from ai_coach import AICoach

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de conversación
WAITING_GOAL, WAITING_PROGRESS, WAITING_MOOD = range(3)

class MotivationalBot:
    def __init__(self):
        self.db = Database()
        self.ai_coach = AICoach(os.getenv('GROQ_API_KEY'))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Bienvenida"""
        user = update.effective_user
        
        # Registrar usuario en la base de datos
        self.db.add_user(user.id, user.username, user.first_name)
        
        welcome_message = f"""
¡Hola {user.first_name}! 👋

Soy tu coach motivacional personal. Estoy aquí para ayudarte a:
✅ Definir y seguir tus objetivos
💪 Mantenerte motivado/a cada día
📈 Celebrar tu progreso
🎯 Superar obstáculos

Comandos disponibles:
/objetivo - Añadir un nuevo objetivo
/progreso - Registrar tu progreso diario
/estado - Ver tus objetivos y progreso
/motivacion - Recibir un mensaje motivacional
/ayuda - Ver todos los comandos

¿Listo/a para empezar tu viaje hacia el éxito?
        """
        
        # Teclado con opciones rápidas
        keyboard = [
            [KeyboardButton("🎯 Nuevo Objetivo"), KeyboardButton("📊 Mi Progreso")],
            [KeyboardButton("💪 Motivación"), KeyboardButton("❓ Ayuda")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ayuda"""
        help_text = """
🤖 **Comandos del Coach Motivacional:**

/start - Iniciar el bot
/objetivo - Añadir un nuevo objetivo personal
/progreso - Registrar tu progreso del día
/estado - Ver tus objetivos actuales y progreso
/motivacion - Recibir un mensaje motivacional personalizado
/ayuda - Mostrar esta ayuda

📱 **Botones rápidos:**
• 🎯 Nuevo Objetivo - Crear un objetivo
• 📊 Mi Progreso - Ver tu evolución
• 💪 Motivación - Mensaje inspirador
• ❓ Ayuda - Mostrar comandos

💡 **Consejos:**
- Sé específico con tus objetivos
- Registra tu progreso diariamente
- Celebra los pequeños logros
- No te rindas en los días difíciles

¡Estoy aquí para apoyarte en tu crecimiento personal! 🚀
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def add_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar proceso de añadir objetivo"""
        await update.message.reply_text(
            "🎯 ¡Genial! Vamos a definir tu nuevo objetivo.\n\n"
            "Describe tu objetivo de forma específica. Por ejemplo:\n"
            "• 'Hacer ejercicio 30 minutos, 4 veces por semana'\n"
            "• 'Leer 2 libros de desarrollo personal este mes'\n"
            "• 'Ahorrar €500 para mis vacaciones en 3 meses'\n\n"
            "¿Cuál es tu objetivo?"
        )
        return WAITING_GOAL
    
    async def process_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar el objetivo recibido"""
        user_id = update.effective_user.id
        goal_text = update.message.text
        
        # Analizar el objetivo con IA
        analysis = self.ai_coach.analyze_goal(goal_text)
        
        # Guardar en base de datos (categoría por defecto)
        goal_id = self.db.add_goal(user_id, goal_text, "", "personal")
        
        response = f"""
✅ **Objetivo registrado exitosamente!**

🎯 **Tu objetivo:** {goal_text}

📋 **Análisis del coach:**
{analysis.get('analysis', 'Objetivo bien definido')}

💡 **Sugerencias:**
"""
        
        for suggestion in analysis.get('suggestions', []):
            response += f"• {suggestion}\n"
        
        response += "\n🚀 **Primeros pasos recomendados:**\n"
        for step in analysis.get('steps', []):
            response += f"• {step}\n"
        
        response += "\n¡Ahora usa /progreso para registrar tu avance diario! 💪"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return ConversationHandler.END
    async def check_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar check-in de progreso diario"""
        user_id = update.effective_user.id
        goals = self.db.get_user_goals(user_id)
        
        if not goals:
            await update.message.reply_text(
                "🤔 Aún no tienes objetivos definidos.\n"
                "Usa /objetivo para crear tu primer objetivo."
            )
            return ConversationHandler.END
        
        # Mostrar objetivos actuales
        goals_text = "📋 **Tus objetivos actuales:**\n\n"
        for i, goal in enumerate(goals, 1):
            goals_text += f"{i}. {goal[1]}\n"
        
        goals_text += "\n💭 Cuéntame sobre tu progreso hoy. ¿Qué lograste? ¿Cómo te sientes?"
        
        await update.message.reply_text(goals_text, parse_mode='Markdown')
        return WAITING_PROGRESS
    
    async def process_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar el progreso reportado"""
        progress_text = update.message.text
        
        await update.message.reply_text(
            "😊 ¿Cómo calificarías tu estado de ánimo hoy?\n\n"
            "1️⃣ Muy bajo\n"
            "2️⃣ Bajo\n"
            "3️⃣ Regular\n"
            "4️⃣ Bueno\n"
            "5️⃣ Excelente\n\n"
            "Envía un número del 1 al 5:"
        )
        
        # Guardar el progreso temporalmente
        context.user_data['progress_text'] = progress_text
        return WAITING_MOOD
    
    async def process_mood(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar el estado de ánimo y generar respuesta motivacional"""
        user_id = update.effective_user.id
        mood_text = update.message.text
        
        try:
            mood_score = int(mood_text)
            if mood_score < 1 or mood_score > 5:
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "Por favor, envía un número del 1 al 5 para tu estado de ánimo."
            )
            return WAITING_MOOD
        
        # Obtener datos del contexto
        progress_text = context.user_data.get('progress_text', '')
        goals = self.db.get_user_goals(user_id)
        recent_progress = self.db.get_user_progress(user_id, 3)
        
        # Registrar progreso en base de datos
        if goals:
            self.db.add_daily_progress(user_id, goals[0][0], progress_text, mood_score)
        
        # Generar respuesta motivacional con IA
        user_context = {
            'goals': [goal[1] for goal in goals],
            'recent_progress': progress_text,
            'mood': mood_score,
            'current_situation': 'Check-in diario'
        }
        
        motivational_message = self.ai_coach.generate_motivational_message(user_context)
        
        # Añadir emojis según el estado de ánimo
        mood_emoji = ["😔", "😐", "🙂", "😊", "🤩"][mood_score - 1]
        
        response = f"""
✅ **Progreso registrado!** {mood_emoji}

{motivational_message}

📊 Usa /estado para ver tu evolución completa.
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return ConversationHandler.END
    
    async def show_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar estado actual de objetivos y progreso"""
        user_id = update.effective_user.id
        goals = self.db.get_user_goals(user_id)
        recent_progress = self.db.get_user_progress(user_id, 7)
        
        if not goals:
            await update.message.reply_text(
                "🤔 Aún no tienes objetivos definidos.\n"
                "Usa /objetivo para crear tu primer objetivo."
            )
            return
        
        # Mostrar objetivos
        status_text = "📊 **Tu Estado Actual**\n\n"
        status_text += "🎯 **Objetivos Activos:**\n"
        
        for i, goal in enumerate(goals, 1):
            status_text += f"{i}. {goal[1]}\n"
        
        # Mostrar progreso reciente
        if recent_progress:
            status_text += "\n📈 **Progreso Reciente:**\n"
            for progress in recent_progress[:3]:  # Últimos 3 registros
                date = progress[2]
                mood = "😔😐🙂😊🤩"[progress[1] - 1] if progress[1] else "😐"
                status_text += f"• {date}: {progress[0][:50]}... {mood}\n"
        
        status_text += "\n💪 ¡Sigue así! Cada paso cuenta hacia tu éxito."
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def get_motivation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generar mensaje motivacional instantáneo"""
        user_id = update.effective_user.id
        goals = self.db.get_user_goals(user_id)
        recent_progress = self.db.get_user_progress(user_id, 3)
        
        user_context = {
            'goals': [goal[1] for goal in goals] if goals else ['Crecimiento personal'],
            'recent_progress': recent_progress[0][0] if recent_progress else 'Buscando motivación',
            'mood': 'Neutral',
            'current_situation': 'Solicitud de motivación'
        }
        
        motivational_message = self.ai_coach.generate_motivational_message(user_context)
        
        await update.message.reply_text(f"💪 {motivational_message}")
    
    async def handle_quick_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar los botones rápidos del teclado"""
        text = update.message.text
        
        if text == "🎯 Nuevo Objetivo":
            return await self.add_goal(update, context)
        elif text == "📊 Mi Progreso":
            return await self.check_progress(update, context)
        elif text == "💪 Motivación":
            await self.get_motivation(update, context)
        elif text == "❓ Ayuda":
            await self.help_command(update, context)
        else:
            # Respuesta por defecto para mensajes no reconocidos
            await update.message.reply_text(
                "🤔 No entendí ese mensaje. Usa los botones del menú o /ayuda para ver los comandos disponibles."
            )
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancelar conversación actual"""
        await update.message.reply_text(
            "❌ Operación cancelada. Usa /ayuda para ver los comandos disponibles."
        )
        return ConversationHandler.END

def main():
    """Función principal para ejecutar el bot"""
    
    # Verificar variables de entorno
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not bot_token or not groq_key:
        print("❌ Error: Faltan variables de entorno.")
        print("Crea un archivo .env con TELEGRAM_BOT_TOKEN y GROQ_API_KEY")
        return
    
    # Crear instancia del bot
    bot = MotivationalBot()
    
    # Crear aplicación
    application = Application.builder().token(bot_token).build()
    
    # Manejador de conversación para objetivos
    goal_handler = ConversationHandler(
        entry_points=[CommandHandler('objetivo', bot.add_goal)],
        states={
            WAITING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.process_goal)],
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)],
    )
    
    # Manejador de conversación para progreso
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
    
    # Manejador para botones rápidos y mensajes generales
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_quick_buttons))
    
    # Iniciar el bot
    print("🤖 Coach Motivacional iniciado...")
    print("Presiona Ctrl+C para detener")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()