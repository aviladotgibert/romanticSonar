import sqlite3
import json
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', '/app/data/romantic_bot.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp DATETIME,
                user_message TEXT,
                bot_response TEXT,
                context TEXT,
                emotion TEXT
            )
        ''')
        
        # Tabla de perfiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferences TEXT,
                relationship_stage TEXT,
                important_dates TEXT,
                first_interaction DATETIME,
                last_interaction DATETIME,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de recuerdos importantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                memory_type TEXT,
                content TEXT,
                importance INTEGER,
                timestamp DATETIME
            )
        ''')
        
        # Índices para mejor rendimiento
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversations_user 
            ON conversations(user_id, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_memories_user 
            ON memories(user_id, importance)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_interaction(self, user_id, user_message, bot_response, context=None, emotion=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, timestamp, user_message, bot_response, context, emotion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, timestamp, user_message, bot_response, 
              json.dumps(context) if context else None, emotion))
        
        # Actualizar perfil
        cursor.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            cursor.execute('''
                UPDATE user_profiles 
                SET last_interaction = ?, total_messages = total_messages + 1
                WHERE user_id = ?
            ''', (timestamp, user_id))
        else:
            cursor.execute('''
                INSERT INTO user_profiles (user_id, first_interaction, last_interaction, total_messages)
                VALUES (?, ?, ?, 1)
            ''', (user_id, timestamp, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp, emotion
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        return list(reversed(results))
    
    def get_user_profile(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_user_profile(self, user_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            for key, value in kwargs.items():
                if key in ['name', 'relationship_stage']:
                    cursor.execute(
                        f'UPDATE user_profiles SET {key} = ? WHERE user_id = ?',
                        (value, user_id)
                    )
                elif key in ['preferences', 'important_dates']:
                    cursor.execute(
                        f'UPDATE user_profiles SET {key} = ? WHERE user_id = ?',
                        (json.dumps(value), user_id)
                    )
        else:
            cursor.execute('''
                INSERT INTO user_profiles (user_id, name, preferences, relationship_stage, important_dates)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                kwargs.get('name', ''),
                json.dumps(kwargs.get('preferences', {})),
                kwargs.get('relationship_stage', 'getting_to_know'),
                json.dumps(kwargs.get('important_dates', {}))
            ))
        
        conn.commit()
        conn.close()
    
    def add_memory(self, user_id, memory_type, content, importance=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories (user_id, memory_type, content, importance, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, memory_type, content, importance, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_important_memories(self, user_id, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT memory_type, content, timestamp
            FROM memories
            WHERE user_id = ?
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_stats(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_messages, first_interaction, last_interaction
            FROM user_profiles
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result if result else (0, None, None)