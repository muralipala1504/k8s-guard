import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json

class Database:
    """SQLite database for action history with 7-day free limit"""
    
    def __init__(self, db_path: str, is_pro: bool = False):
        self.db_path = Path(db_path)
        self.is_pro = is_pro
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                namespace TEXT,
                status TEXT NOT NULL,
                details TEXT,
                triggered_by TEXT DEFAULT 'auto'
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON actions(timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def add_action(self, action_type: str, resource_type: str, 
                   resource_name: str, namespace: str = '', 
                   status: str = 'success', details: str = '') -> int:
        """Add an action to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO actions (timestamp, action_type, resource_type, 
                               resource_name, namespace, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), action_type, resource_type,
              resource_name, namespace, status, details))
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if not self.is_pro:
            self._cleanup_old_records()
        
        return action_id
    
    def _cleanup_old_records(self):
        """Delete records older than 7 days for free tier"""
        cutoff = datetime.now() - timedelta(days=7)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM actions 
            WHERE timestamp < ?
        ''', (cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            print(f"[INFO] Cleaned up {deleted} old actions (7-day limit)")
    
    def get_actions(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get recent actions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM actions 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get action statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM actions')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT action_type, COUNT(*) as count 
            FROM actions 
            GROUP BY action_type
        ''')
        by_type = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_actions': total,
            'by_type': dict(by_type),
            'is_pro': self.is_pro,
            'storage_limit': 'Unlimited' if self.is_pro else '7 days'
        }
