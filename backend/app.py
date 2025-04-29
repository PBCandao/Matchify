#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import uuid
from flask_socketio import SocketIO

import models

import graph_logic
import contacts
import recommendations
import notifications
import os
import io, json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from fake_data import seed_data
import db

# you need a secret key for sessions to work
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Catch-all route for serving the SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    full_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
# Initialize database, migrate auth schema, and seed demo data
DEMO_MODE = os.environ.get('DEMO_MODE') == 'true'
db.init_db()
db.migrate_auth_fields()
if DEMO_MODE:
    # Seed demo data and default user
    seed_data()
    db.set_user_username('me', 'me')
    pwd_hash = generate_password_hash('password')
    db.set_user_password('me', pwd_hash)
# Load in-memory graph from SQLite
graph_logic.load_data_from_db()

"""
Require login for protected routes, exempting login and register pages.
"""
@app.before_request
def require_login():
    # Endpoints that do not require login
    exempt_endpoints = ('login', 'register', 'static')
    if request.endpoint in exempt_endpoints:
        return
    if 'user_id' not in session:
        return redirect('/login')

# Login route for demo user
@app.route('/login', methods=['POST'])
def login():
    # POST: authenticate credentials
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return redirect('/login')
    user = db.get_user_by_username(username)
    if not user or not check_password_hash(user.get('password_hash', ''), password):
        return redirect('/login')
    # Mark user as logged in
    session['user_id'] = user['id']
    return redirect('/')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Registration route for new users
@app.route('/register', methods=['POST'])
def register():
    # POST: create new user account
    name = request.form.get('name') or ''
    username = request.form.get('username')
    password = request.form.get('password')
    # Basic validation
    if not username or not password:
        return redirect('/register')
    # Check if username already exists
    existing = db.get_user_by_username(username)
    if existing:
        # Username taken, redirect (could flash a message)
        return redirect('/register')
    # Create new user
    new_id = uuid.uuid4().hex
    # Default values for new profile
    avatar_url = ''
    roles = []
    main_role = ''
    db.add_user_db(new_id, name, avatar_url, roles, main_role)
    # Set auth fields
    db.set_user_username(new_id, username)
    pwd_hash = generate_password_hash(password)
    db.set_user_password(new_id, pwd_hash)
    # Log in new user
    session['user_id'] = new_id
    return redirect('/')
@app.route('/api/roles')
def api_roles():
    """Return distinct list of all roles from users."""
    roles = db.get_all_roles()
    return jsonify({'roles': roles})
# Initialize notifications module with SocketIO instance
notifications.init_app(socketio)
 

@app.route('/graph')
def get_graph():
    user_id = request.args.get('user')
    depth = int(request.args.get('depth', 1))
    nodes, links = graph_logic.get_graph(user_id, depth)
    return jsonify({'nodes': nodes, 'links': links})
 
@app.route('/path')
def get_path():
    # Return the shortest connection path between two users
    from_id = request.args.get('from')
    to_id = request.args.get('to')
    if not from_id or not to_id:
        return jsonify({'path': []}), 400
    path = graph_logic.get_path(from_id, to_id)
    return jsonify({'path': path})
 
@app.route('/request_connection', methods=['POST'])
def request_connection():
    """
    Alias for introductory connection requests.
    """
    data = request.get_json() or {}
    # Expect fields: from, to, via
    result = contacts.request_intro(data)
    return jsonify(result)

@app.route('/upload_contacts', methods=['POST'])
def upload_contacts():
    file = request.files.get('file')
    matches = contacts.process_upload(file)
    return jsonify({'matches': matches})

@app.route('/request_intro', methods=['POST'])
def request_intro():
    data = request.get_json() or {}
    result = contacts.request_intro(data)
    return jsonify(result)

@app.route('/api/location', methods=['POST'])
def api_location():
    """Update user location and broadcast via WebSocket."""
    data = request.get_json() or {}
    lat = data.get('lat')
    lng = data.get('lng')
    if lat is None or lng is None:
        return jsonify({'error': 'Missing lat/lng'}), 400
    # Persist
    db.update_user_location('me', lat, lng)
    # Broadcast to all
    socketio.emit('location_update', {'user_id': 'me', 'lat': lat, 'lng': lng}, broadcast=True)
    return jsonify({'status': 'ok'})

@app.route('/api/map_nodes')
def api_map_nodes():
    """Return users nearby based on query params."""
    try:
        radius = float(request.args.get('radius', 5.0))
    except ValueError:
        radius = 5.0
    roles_param = request.args.get('roles', '')
    roles = [r for r in roles_param.split(',') if r]
    online_only = request.args.get('onlineOnly') == 'true'
    # For privacy, we exclude 'me' if offline/invisible
    exclude = 'me'
    # Get current user's location
    # For simplicity, use location posted in user_locations
    # Fetch from DB
    loc = None
    conn = db.get_connection(); c = conn.cursor();
    row = c.execute('SELECT lat, lng FROM user_locations WHERE user_id = ?', ('me',)).fetchone(); conn.close()
    if row:
        center_lat, center_lng = row['lat'], row['lng']
    else:
        return jsonify({'users': []})
    users = db.get_nearby_users(center_lat, center_lng, radius, roles or None, online_only, exclude_user=exclude)
    return jsonify({'users': users})
@app.route('/api/ai_search', methods=['POST'])
def api_ai_search():
    """Stub AI search endpoint."""
    data = request.get_json() or {}
    query = data.get('query', '')
    # TODO: integrate AI service
    results = []
    return jsonify({'results': results})

@app.route('/approve_intro', methods=['POST'])
def approve_intro():
    data = request.get_json() or {}
    result = contacts.approve_intro(data)
    return jsonify(result)

@app.route('/suggestions')
def suggestions():
    user_id = request.args.get('user')
    suggestions_list = recommendations.get_suggestions(user_id)
    return jsonify({'suggestions': suggestions_list})

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json() or {}
    user_id = data.get('id')
    name = data.get('name')
    roles = data.get('roles')
    phone_hash = data.get('phoneHash')
    graph_logic.add_user(user_id, name=name, roles=roles, phoneHash=phone_hash)
    return jsonify({'status': 'ok'})

@app.route('/add_relationship', methods=['POST'])
def add_relationship():
    data = request.get_json() or {}
    source = data.get('source')
    target = data.get('target')
    weight = data.get('weight')
    status = data.get('status')
    graph_logic.add_relationship(source, target, weight=weight, status=status)
    return jsonify({'status': 'ok'})

# WebSocket notifications are emitted via notifications module
## Profile data is persisted in SQLite; no in-memory PROFILES

@app.route('/profile/me')
def get_my_profile():
    # Return own profile with list of direct contacts
    profile = db.get_user_profile('me')
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    # Include contacts list (IDs of direct relationships)
    contacts = db.get_direct_contacts('me')
    profile['contacts'] = [c['id'] for c in contacts]
    return jsonify(profile)

@app.route('/profile/<user_id>')
def get_user_profile(user_id):
    profile = db.get_user_profile(user_id)
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(profile)

@app.route('/api/contacts')
def get_contacts():
    # Direct contacts based on relationships
    contacts_list = db.get_direct_contacts('me')
    # For each contact, include their own contacts (for common friends calculation)
    for c in contacts_list:
        subs = db.get_direct_contacts(c['id'])
        c['contacts'] = [s['id'] for s in subs]
    return jsonify(contacts_list)

@app.route('/profile/<user_id>', methods=['POST'])
def update_user_profile(user_id):
    # Update persisted user profile
    existing = db.get_user_profile(user_id)
    if not existing:
        return jsonify({'error': 'User not found'}), 404
    updates = {}
    # Text fields
    for field in ['bio_long', 'looking_for', 'offering', 'telegram']:
        if field in request.form:
            updates[field] = request.form.get(field)
    # Roles and main role
    roles = request.form.getlist('roles')
    if roles:
        # Reorder main_role to front if provided
        main_role = request.form.get('main_role')
        if main_role and main_role in roles:
            roles.insert(0, roles.pop(roles.index(main_role)))
        updates['roles'] = roles
        updates['main_role'] = roles[0]
    # Avatar upload
    avatar = request.files.get('avatar')
    if avatar and avatar.filename:
        filename = secure_filename(avatar.filename)
        ext = os.path.splitext(filename)[1]
        new_name = f"{user_id}{ext}"
        save_path = os.path.join(app.static_folder, 'assets', new_name)
        avatar.save(save_path)
        avatar_url = f"/assets/{new_name}"
        updates['avatar_url'] = avatar_url
    # Persist updates
    if updates:
        db.update_user_profile_db(user_id, **updates)
    # Return updated profile
    profile = db.get_user_profile(user_id)
    return jsonify({'status': 'ok', 'profile': profile})
    
## Notifications Page and API
@app.route('/notifications')
def serve_notifications_page():
    # Serve static notifications center page
    return app.send_static_file('notifications.html')

@app.route('/api/notifications')
def api_get_notifications():
    """Return JSON list of ActivityLog entries for the current user ('me')."""
    logs = notifications.get_logs('me')
    return jsonify({'notifications': logs})

@app.route('/api/notifications/mark_all_read', methods=['POST'])
def api_mark_all_read():
    # Mark all notifications read in database
    user = session.get('user_id')
    db.mark_all_notifications_read(user)
    return '', 204

@app.route('/api/notifications/<event_id>/read', methods=['POST'])
def api_mark_read(event_id):
    # Mark individual notification read in database
    db.mark_notification_read(event_id)
    return '', 204

@app.route('/api/notifications/<event_id>/approve', methods=['POST'])
def api_approve_intro(event_id):
    # Stub: mark an introduction request approved
    return '', 204

@app.route('/api/notifications/<event_id>/decline', methods=['POST'])
def api_decline_intro(event_id):
    # Stub: mark an introduction request declined
    return '', 204
  
@app.route('/api/settings')
def api_get_settings():
    """Return current user's profile and preferences"""
    profile = db.get_user_profile('me') or {}
    prefs = db.get_user_preferences('me')
    return jsonify({'profile': profile, 'preferences': prefs})

@app.route('/api/settings', methods=['PUT'])
def api_update_settings():
    """Update current user's profile and preferences"""
    data = request.get_json() or {}
    # Profile fields
    fields = ['name', 'bio_long', 'telegram', 'avatar_url', 'roles', 'main_role']
    updates = {k: data[k] for k in fields if k in data}
    if updates:
        db.update_user_profile_db('me', **updates)
    # Preferences
    if 'preferences' in data and isinstance(data['preferences'], dict):
        db.update_user_preferences_db('me', data['preferences'])
    return jsonify({'status': 'ok'})

@app.route('/api/upload_avatar', methods=['POST'])
def api_upload_avatar():
    """Handle avatar file upload and return URL"""
    file = request.files.get('avatar')
    if not file or not file.filename:
        return jsonify({'error': 'No file uploaded'}), 400
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    new_name = f"me{ext}"
    save_path = os.path.join(app.static_folder, 'assets', new_name)
    file.save(save_path)
    url = f"/static/assets/{new_name}"
    # Persist avatar_url
    db.update_user_profile_db('me', avatar_url=url)
    return jsonify({'url': url})

# Advanced Settings & Account Management APIs
@app.route('/api/preferences', methods=['GET', 'POST'])
def api_preferences():
    # Preferences for current user ('me')
    if request.method == 'GET':
        prefs = db.get_user_preferences('me')
        return jsonify(prefs)
    data = request.get_json() or {}
    # Merge and save preferences
    current = db.get_user_preferences('me')
    current.update(data)
    db.update_user_preferences_db('me', current)
    return '', 204

@app.route('/api/export_data', methods=['GET'])
def api_export_data():
    # Export user's profile, contacts, and activity log as JSON
    profile = db.get_user_profile('me') or {}
    contacts = db.get_direct_contacts('me')
    activity = notifications.get_logs('me')
    export = {'profile': profile, 'contacts': contacts, 'activity': activity}
    buf = io.BytesIO()
    buf.write(json.dumps(export, indent=2).encode('utf-8'))
    buf.seek(0)
    return send_file(buf,
                     download_name='me_matchify_export.json',
                     as_attachment=True,
                     mimetype='application/json')

@app.route('/api/delete_account', methods=['POST'])
def api_delete_account():
    # Delete user and related data
    # Remove from DB
    conn = db.get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM relationships WHERE user1_id = ? OR user2_id = ?', ('me','me'))
    c.execute('DELETE FROM users WHERE id = ?', ('me',))
    conn.commit()
    conn.close()
    # Remove from in-memory graph
    try:
        graph_logic.G.remove_node('me')
    except Exception:
        pass
    # Remove activity logs
    notifications.activity_logs[:] = [e for e in notifications.activity_logs if e.get('user_id') != 'me']
    # Clear session if used
    session.clear()
    return jsonify({'deleted': True})

@app.route('/api/meetups', methods=['POST'])
def api_meetups():
    """Create a new meetup and send invites."""
    data = request.get_json() or {}
    title = data.get('title')
    time = data.get('time')
    location = data.get('location', {})
    invitees = data.get('invitees', [])
    meetup_id = str(uuid.uuid4())
    # Insert meetup
    conn = db.get_connection(); c = conn.cursor()
    c.execute('INSERT INTO meetups (id, host, title, lat, lng, time) VALUES (?,?,?,?,?,?)',
              (meetup_id, 'me', title, location.get('lat'), location.get('lng'), time))
    # Insert invites
    for inv in invitees:
        c.execute('INSERT OR REPLACE INTO meetup_invites (meetup_id, invitee, status) VALUES (?,?,?)',
                  (meetup_id, inv, 'pending'))
        # Notify invitee
        payload = {
            'meetup_id': meetup_id,
            'from': 'me',
            'title': title,
            'location': location,
            'time': time
        }
        socketio.emit('meetup_invite', payload, room=inv)
    conn.commit(); conn.close()
    return jsonify({'meetup_id': meetup_id})

@app.route('/api/meetups/<meetup_id>/route', methods=['GET'])
def api_meetup_route(meetup_id):
    """Return route waypoints for a meetup."""
    conn = db.get_connection(); c = conn.cursor()
    row = c.execute('SELECT lat, lng FROM meetups WHERE id = ?', (meetup_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'route': []}), 404
    # Stub route: host location -> meetup location (same here)
    route = [ {'lat': row['lat'], 'lng': row['lng']} ]
    return jsonify({'route': route})

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000)
