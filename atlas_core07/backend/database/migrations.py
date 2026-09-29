import os
from datetime import datetime

MIGRATIONS = {
    '001_initial_schema': 'Handled in db.py',
    '002_add_indexes': 'CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);',
}

def init_migrations():
    """Initialize migrations"""
    from .db import get_db
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            name TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    ''')
    db.commit()
    
    for name, sql in MIGRATIONS.items():
        cursor.execute('SELECT name FROM migrations WHERE name = ?', (name,))
        if not cursor.fetchone():
            if sql != 'Handled in db.py':
                cursor.executescript(sql)
            cursor.execute('INSERT INTO migrations (name, applied_at) VALUES (?, ?)',
                         (name, datetime.utcnow().isoformat()))
            db.commit()
            print(f'Applied migration: {name}')
    
    db.close()
