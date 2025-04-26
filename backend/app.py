#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_socketio import SocketIO

import models

import graph_logic
import contacts
import recommendations
import notifications
import os
from werkzeug.utils import secure_filename
from fake_data import seed_data

app = Flask(__name__, static_folder='../frontend', static_url_path='/static')
app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
# Initialize database and seed data
import db
seed_data()
# Load in-memory graph from SQLite
graph_logic.load_data_from_db()
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/contacts')
def serve_contacts():
    return app.send_static_file('contacts.html')
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

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000)
