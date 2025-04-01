# api/database.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

class ChatDatabase:
    def __init__(self, db_path: str = "chat_history.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_message(self, session_id: str, role: str, message: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (session_id, role, message)
            VALUES (?, ?, ?)
        ''', (session_id, role, message))
        self.conn.commit()

    def get_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT role, message FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp
            LIMIT ?
        ''', (session_id, limit))
        # Reverse to maintain chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(cursor.fetchall())]
    
    def get_all_sessions(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT session_id FROM chat_history
        ''')
        return [row[0] for row in cursor.fetchall()]