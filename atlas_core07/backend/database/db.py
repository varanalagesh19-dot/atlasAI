import sqlite3
import os
from datetime import datetime

DATABASE = 'atlas_core07.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def dict_from_row(row):
    """Convert sqlite3.Row to dict"""
    return dict(row) if row else None

def init_db():
    """Initialize database schema"""
    db = get_db()
    cursor = db.cursor()
    
    # Conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            model TEXT DEFAULT 'atlas_smart',
            pinned INTEGER DEFAULT 0
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    db.commit()
    db.close()

def create_conversation(title, model='atlas_smart'):
    """Create new conversation"""
    from uuid import uuid4
    db = get_db()
    cursor = db.cursor()
    
    conv_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO conversations (id, title, created_at, updated_at, model)
        VALUES (?, ?, ?, ?, ?)
    ''', (conv_id, title, now, now, model))
    
    db.commit()
    db.close()
    
    return conv_id

def get_conversations():
    """Get all conversations"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at, model, pinned
        FROM conversations
        ORDER BY updated_at DESC
    ''')
    
    conversations = [dict_from_row(row) for row in cursor.fetchall()]
    db.close()
    
    return conversations

def get_conversation(conv_id):
    """Get specific conversation with messages"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at, model, pinned
        FROM conversations
        WHERE id = ?
    ''', (conv_id,))
    
    conv = dict_from_row(cursor.fetchone())
    
    if not conv:
        db.close()
        return None
    
    cursor.execute('''
        SELECT id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at
    ''', (conv_id,))
    
    conv['messages'] = [dict_from_row(row) for row in cursor.fetchall()]
    db.close()
    
    return conv

def add_message(conv_id, role, content):
    """Add message to conversation"""
    from uuid import uuid4
    db = get_db()
    cursor = db.cursor()
    
    msg_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (msg_id, conv_id, role, content, now))
    
    cursor.execute('''
        UPDATE conversations
        SET updated_at = ?
        WHERE id = ?
    ''', (now, conv_id))
    
    db.commit()
    db.close()
    
    return {'id': msg_id, 'role': role, 'content': content, 'created_at': now}

def update_conversation(conv_id, title=None, model=None, pinned=None):
    """Update conversation"""
    db = get_db()
    cursor = db.cursor()
    now = datetime.utcnow().isoformat()
    
    if title:
        cursor.execute('UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?',
                      (title, now, conv_id))
    if model:
        cursor.execute('UPDATE conversations SET model = ?, updated_at = ? WHERE id = ?',
                      (model, now, conv_id))
    if pinned is not None:
        cursor.execute('UPDATE conversations SET pinned = ?, updated_at = ? WHERE id = ?',
                      (pinned, now, conv_id))
    
    db.commit()
    db.close()

def delete_conversation(conv_id):
    """Delete conversation and messages"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conv_id,))
    cursor.execute('DELETE FROM conversations WHERE id = ?', (conv_id,))
    
    db.commit()
    db.close()

def search_conversations(query):
    """Search conversations by title or content"""
    db = get_db()
    cursor = db.cursor()
    
    query_pattern = f"%{query}%"
    
    cursor.execute('''
        SELECT DISTINCT c.id, c.title, c.created_at, c.updated_at, c.model, c.pinned
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.title LIKE ? OR m.content LIKE ?
        ORDER BY c.updated_at DESC
    ''', (query_pattern, query_pattern))
    
    conversations = [dict_from_row(row) for row in cursor.fetchall()]
    db.close()
    
    return conversations
