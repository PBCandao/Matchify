import sqlite3
import json
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def get_connection():
    """
    Get a SQLite connection with row factory.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database tables if they do not exist.
    """
    conn = get_connection()
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            avatar_url TEXT,
            main_role TEXT,
            roles TEXT,
            bio_long TEXT,
            looking_for TEXT,
            offering TEXT,
            telegram TEXT,
            created_at TEXT
        )
    ''')
    # Relationships table (undirected edges stored once)
    c.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            user1_id TEXT,
            user2_id TEXT,
            weight REAL,
            status TEXT,
            lastInteraction TEXT,
            PRIMARY KEY (user1_id, user2_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user_db(user_id, name, avatar_url, roles, main_role,
                bio_long=None, looking_for=None, offering=None, telegram=None):
    """
    Insert or update a user record.
    roles: list of role strings
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users
        (id, name, avatar_url, main_role, roles, bio_long, looking_for, offering, telegram, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        name,
        avatar_url,
        main_role,
        json.dumps(roles or []),
        bio_long,
        looking_for,
        offering,
        telegram,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def add_relationship_db(u1, u2, weight=1.0, status='connected', lastInteraction=None):
    """
    Insert or update an undirected relationship (store both directions).
    """
    if lastInteraction is None:
        lastInteraction = datetime.utcnow().isoformat()
    conn = get_connection()
    c = conn.cursor()
    # Store both directions for easier querying
    for a, b in ((u1, u2), (u2, u1)):
        c.execute('''
            INSERT OR REPLACE INTO relationships
            (user1_id, user2_id, weight, status, lastInteraction)
            VALUES (?, ?, ?, ?, ?)
        ''', (a, b, weight, status, lastInteraction))
    conn.commit()
    conn.close()

def get_all_users():
    """
    Return list of all users as dicts.
    """
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute('SELECT * FROM users').fetchall()
    conn.close()
    users = []
    for row in rows:
        u = dict(row)
        # Parse roles JSON
        try:
            u['roles'] = json.loads(u.get('roles') or '[]')
        except Exception:
            u['roles'] = []
        users.append(u)
    return users

def get_all_relationships():
    """
    Return list of all relationships as dicts.
    """
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute(
        'SELECT user1_id, user2_id, weight, status, lastInteraction FROM relationships'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_profile(user_id):
    """
    Return a single user profile dict or None.
    """
    conn = get_connection()
    c = conn.cursor()
    row = c.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not row:
        return None
    u = dict(row)
    try:
        u['roles'] = json.loads(u.get('roles') or '[]')
    except Exception:
        u['roles'] = []
    return u

def get_direct_contacts(user_id):
    """
    Return list of user profiles directly connected to given user.
    """
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute('''
        SELECT u.* FROM relationships r
        JOIN users u ON u.id = r.user2_id
        WHERE r.user1_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    contacts = []
    for row in rows:
        u = dict(row)
        try:
            u['roles'] = json.loads(u.get('roles') or '[]')
        except Exception:
            u['roles'] = []
        contacts.append(u)
    return contacts

def update_user_profile_db(user_id, **fields):
    """
    Update one or more profile fields for a user.
    Supported: avatar_url, bio_long, looking_for, offering, telegram, roles, main_role
    """
    if not fields:
        return
    conn = get_connection()
    c = conn.cursor()
    sets = []
    vals = []
    for key, val in fields.items():
        if key == 'roles':
            sets.append('roles = ?')
            vals.append(json.dumps(val))
        else:
            sets.append(f'{key} = ?')
            vals.append(val)
    vals.append(user_id)
    query = f'UPDATE users SET {", ".join(sets)} WHERE id = ?'
    c.execute(query, vals)
    conn.commit()
    conn.close()