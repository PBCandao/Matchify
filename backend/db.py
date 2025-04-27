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
    # Users table (add preferences JSON)
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
            preferences TEXT,
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
    # User locations for map (lat,lng)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_locations (
            user_id TEXT PRIMARY KEY,
            lat REAL,
            lng REAL,
            updated_at TEXT
        )
    ''')
    # Meetups and invites
    c.execute('''
        CREATE TABLE IF NOT EXISTS meetups (
            id TEXT PRIMARY KEY,
            host TEXT,
            title TEXT,
            lat REAL,
            lng REAL,
            time TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS meetup_invites (
            meetup_id TEXT,
            invitee TEXT,
            status TEXT,
            PRIMARY KEY (meetup_id, invitee)
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
        # Parse preferences JSON
        try:
            u['preferences'] = json.loads(u.get('preferences') or '{}')
        except Exception:
            u['preferences'] = {}
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
def get_all_roles():
    """
    Return sorted list of unique roles across all users.
    """
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute('SELECT roles FROM users').fetchall()
    conn.close()
    roles_set = set()
    for row in rows:
        try:
            lst = json.loads(row['roles'] or '[]')
            for r in lst: roles_set.add(r)
        except Exception:
            continue
    return sorted(roles_set)

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
    # Parse preferences JSON
    try:
        u['preferences'] = json.loads(u.get('preferences') or '{}')
    except Exception:
        u['preferences'] = {}
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
::
def get_user_preferences(user_id):
    """
    Return preferences dict for a given user, defaulting to {}.
    """
    u = get_user_profile(user_id)
    if u and 'preferences' in u:
        return u['preferences']
    return {}

def update_user_preferences_db(user_id, preferences):
    """
    Update the preferences JSON for a user.
    preferences: dict
    """
    conn = get_connection()
    c = conn.cursor()
    prefs_json = json.dumps(preferences)
    c.execute('UPDATE users SET preferences = ? WHERE id = ?', (prefs_json, user_id))
    conn.commit()
    conn.close()

def migrate_auth_fields():
    """
    Add authentication columns to users table if missing.
    """
    conn = get_connection()
    c = conn.cursor()
    # Check existing columns
    cols = [row['name'] for row in c.execute("PRAGMA table_info(users)").fetchall()]
    if 'username' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN username TEXT")
    if 'password_hash' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    conn.commit()
    conn.close()

def set_user_password(user_id, password_hash):
    """
    Set the password hash for a user.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

def set_user_username(user_id, username):
    """
    Set the username for a user.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """
    Retrieve a user record by username.
    Returns a dict or None.
    """
    conn = get_connection()
    c = conn.cursor()
    row = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if not row:
        return None
    user = dict(row)
    # Parse roles
    try:
        user['roles'] = json.loads(user.get('roles') or '[]')
    except Exception:
        user['roles'] = []
    # Parse preferences
    try:
        user['preferences'] = json.loads(user.get('preferences') or '{}')
    except Exception:
        user['preferences'] = {}
    return user

def update_user_location(user_id, lat, lng):
    """
    Insert or update a user's latitude/longitude.
    """
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    c.execute('INSERT OR REPLACE INTO user_locations (user_id, lat, lng, updated_at) VALUES (?, ?, ?, ?)',
              (user_id, lat, lng, now))
    conn.commit()
    conn.close()

def get_nearby_users(center_lat, center_lng, radius_km, roles=None, online_only=False, exclude_user=None):
    """
    Return list of users within radius_km of center point.
    roles: list of role strings to filter, or None
    online_only: if True, filter users status=online
    exclude_user: user_id to exclude (e.g. 'me')
    """
    # Haversine formula in SQL
    conn = get_connection()
    c = conn.cursor()
    # Join users and user_locations
    query = '''
    SELECT u.id, u.name, u.avatar_url, u.roles, ul.lat, ul.lng
    FROM user_locations ul
    JOIN users u ON u.id = ul.user_id
    WHERE (? * acos(
          cos(radians(?)) * cos(radians(lat))
          * cos(radians(lng) - radians(?))
          + sin(radians(?)) * sin(radians(lat))
        )) <= ?
    '''
    params = [6371.0, center_lat, center_lng, center_lat, radius_km]
    # Filter roles
    if roles:
        query += ' AND (' + ' OR '.join(["u.roles LIKE '%' || ? || '%'" for _ in roles]) + ')'
        params.extend(roles)
    # Exclude user
    if exclude_user:
        query += ' AND u.id != ?'
        params.append(exclude_user)
    rows = c.execute(query, params).fetchall()
    conn.close()
    users = []
    for row in rows:
        u = dict(row)
        try:
            u['roles'] = json.loads(u['roles'] or '[]')
        except Exception:
            u['roles'] = []
        u['lat'] = row['lat']
        u['lng'] = row['lng']
        # Default status
        u['status'] = 'online'
        users.append(u)
    # Note: online_only not yet implemented
    return users