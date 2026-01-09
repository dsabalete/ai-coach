import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path="coach_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                coaching_style TEXT DEFAULT 'motivacional',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de objetivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                target_date DATE,
                status TEXT DEFAULT 'activo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabla de progreso diario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                goal_id INTEGER,
                progress_text TEXT,
                mood_score INTEGER,
                date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        """Registra un nuevo usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def add_goal(self, user_id, title, description, category, target_date=None):
        """Añade un nuevo objetivo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goals (user_id, title, description, category, target_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, description, category, target_date))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id
    
    def get_user_goals(self, user_id):
        """Obtiene los objetivos activos del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, category, target_date, status
            FROM goals 
            WHERE user_id = ? AND status = 'activo'
            ORDER BY created_at DESC
        ''', (user_id,))
        
        goals = cursor.fetchall()
        conn.close()
        return goals
    
    def add_daily_progress(self, user_id, goal_id, progress_text, mood_score):
        """Registra el progreso diario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO daily_progress (user_id, goal_id, progress_text, mood_score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, goal_id, progress_text, mood_score))
        
        conn.commit()
        conn.close()
    
    def get_user_progress(self, user_id, days=7):
        """Obtiene el progreso reciente del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dp.progress_text, dp.mood_score, dp.date, g.title
            FROM daily_progress dp
            JOIN goals g ON dp.goal_id = g.id
            WHERE dp.user_id = ?
            ORDER BY dp.date DESC
            LIMIT ?
        ''', (user_id, days))
        
        progress = cursor.fetchall()
        conn.close()
        return progress