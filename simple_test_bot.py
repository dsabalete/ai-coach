#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de prueba simplificado para diagnosticar problemas
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from ai_coach import AICoach

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            self.ai_coach = AICoach(groq_key)
        else:
            self.ai_coach = None
            print("⚠️  No se encontró GROQ_API_KEY")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start simple"""
        await update.message.reply_text("¡Hola! Bot de prueba funcionando. Usa /test para probar IA.")
    
    async def test_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /test para probar IA"""
        if not self.ai_coach:
            await update.message.reply_text("❌ AI Coach no disponible - verifica GROQ_API_KEY")
            return
        
        try:
            await update.message.reply_text("🧪 Probando IA...")
            
            # Prueba simple
            test_context = {
                'goals': ['Hacer ejercicio'],
                'recent_progress': 'Hoy caminé 30 minutos',
                'mood': 4,
                'current_situation': 'Prueba'
            }
            
            message = self.ai_coach.generate_motivational_message(test_context)
            await update.message.reply_text(f"✅ IA funcionando:\n\n{message}")
            
        except Exception as e:
            error_msg = f"❌ Error en IA: {str(e)}"
            print(error_msg)
            await update.message.reply_text(error_msg)

def main():
    """Función principal simplificada"""
    
    # Verificar variables de entorno
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado")
        return
    
    if not groq_key:
        print("⚠️  GROQ_API_KEY no encontrado - IA deshabilitada")
    
    # Crear bot
    bot = SimpleBot()
    
    # Crear aplicación
    application = Application.builder().token(bot_token).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("test", bot.test_ai))
    
    # Iniciar
    print("🤖 Bot de prueba iniciado...")
    print("Comandos: /start, /test")
    print("Presiona Ctrl+C para detener")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()