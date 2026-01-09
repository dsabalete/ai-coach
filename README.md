# 🤖 Coach Motivacional - Bot de Telegram

Un bot de Telegram inteligente que actúa como tu coach personal para ayudarte a alcanzar tus objetivos usando IA.

## ✨ Características

- **Definición de objetivos SMART** con análisis de IA
- **Seguimiento diario** de progreso y estado de ánimo
- **Mensajes motivacionales personalizados** generados con Groq AI
- **Base de datos persistente** para historial de progreso
- **Interfaz conversacional** natural y empática
- **Botones rápidos** para facilitar la interacción

## 🚀 Configuración

### 1. Prerrequisitos

- Python 3.8+
- Cuenta de Telegram
- API Key de Groq (gratuita)

### 2. Crear el bot de Telegram

1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Usa `/newbot` y sigue las instrucciones
3. Guarda el token que te proporciona

### 3. Obtener API Key de Groq

1. Ve a [Groq Console](https://console.groq.com/keys)
2. Crea una cuenta gratuita si no tienes una
3. Genera una nueva API key
4. Guárdala de forma segura

### 4. Instalación

```bash
# Clonar o descargar el proyecto
cd coach-motivacional-bot

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus tokens
```

### 5. Configurar variables de entorno

Edita el archivo `.env`:

```env
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
GROQ_API_KEY=tu_api_key_de_groq_aqui
```

## 🎮 Uso

### Ejecutar el bot

```bash
python telegram_bot.py
```

### Comandos disponibles

- `/start` - Iniciar el bot y registro
- `/objetivo` - Añadir un nuevo objetivo personal
- `/progreso` - Registrar progreso diario
- `/estado` - Ver objetivos y progreso actual
- `/motivacion` - Recibir mensaje motivacional
- `/ayuda` - Ver todos los comandos

### Botones rápidos

- 🎯 **Nuevo Objetivo** - Crear objetivo
- 📊 **Mi Progreso** - Registrar avance
- 💪 **Motivación** - Mensaje inspirador
- ❓ **Ayuda** - Mostrar comandos

## 📊 Base de datos

El bot usa SQLite para almacenar:

- **Usuarios**: Información básica y preferencias
- **Objetivos**: Metas definidas por el usuario
- **Progreso diario**: Seguimiento y estado de ánimo

## 🔧 Estructura del proyecto

```
coach-motivacional-bot/
├── telegram_bot.py      # Bot principal de Telegram
├── ai_coach.py          # Lógica de IA y coaching
├── database.py          # Gestión de base de datos
├── requirements.txt     # Dependencias Python
├── .env.example        # Plantilla de configuración
└── README.md           # Este archivo
```

## 🎯 Funcionalidades principales

### Análisis inteligente de objetivos

- Evalúa si los objetivos son SMART
- Sugiere mejoras automáticamente
- Propone pasos concretos para alcanzarlos

### Coaching personalizado

- Mensajes motivacionales adaptados al progreso
- Análisis de estado de ánimo
- Preguntas reflexivas diarias

### Seguimiento de progreso

- Registro diario de avances
- Historial de evolución
- Métricas de estado de ánimo

## 🚀 Próximas mejoras

- [ ] Recordatorios automáticos programados
- [ ] Gráficos de progreso visual
- [ ] Integración con calendarios
- [ ] Múltiples estilos de coaching
- [ ] Exportar datos de progreso
- [ ] Gamificación con logros

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Puedes:

1. Reportar bugs
2. Sugerir nuevas funcionalidades
3. Mejorar la documentación
4. Enviar pull requests

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## ⚠️ Consideraciones

- **Privacidad**: Los datos se almacenan localmente
- **Costos**: Groq ofrece un tier gratuito generoso
- **Límites**: Respeta los límites de rate de las APIs
- **Seguridad**: Mantén tus tokens seguros y privados

---

¡Empieza tu viaje hacia el éxito personal! 🌟
