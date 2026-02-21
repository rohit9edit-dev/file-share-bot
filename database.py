import sqlite3
import logging
from config import logger

class Database:
    def __init__(self, db_path="data/file_share_bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
            ''')
            
            # Create files table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                unique_key TEXT PRIMARY KEY,
                message_id INTEGER NOT NULL
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_user(self, user_id):
        """Add a new user to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_all_users(self):
        """Get all user IDs from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            users = [row[0] for row in cursor.fetchall()]
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
        finally:
            conn.close()
    
    def add_file(self, unique_key, message_id):
        """Add a new file mapping to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO files (unique_key, message_id) VALUES (?, ?)",
                (unique_key, message_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding file {unique_key}: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_file_message_id(self, unique_key):
        """Get message_id for a given unique_key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT message_id FROM files WHERE unique_key = ?",
                (unique_key,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting message_id for {unique_key}: {str(e)}")
            return None
        finally:
            conn.close()
    
    def remove_user(self, user_id):
        """Remove a user from the database (when blocked/deactivated)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing user {user_id}: {str(e)}")
            return False
        finally:
            conn.close()
