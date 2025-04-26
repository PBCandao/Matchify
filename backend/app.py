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
from fake_data import generate_profiles

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
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
# Mock profile data generated dynamically
PROFILES = generate_profiles()

@app.route('/profile/me')
def get_my_profile():
    return jsonify(PROFILES.get('me', {}))

@app.route('/profile/<user_id>')
def get_user_profile(user_id):
    profile = PROFILES.get(user_id)
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(profile)

@app.route('/api/contacts')
def get_contacts():
    me = PROFILES.get('me')
    if not me:
        return jsonify([]), 404
    ids = me.get('contacts', [])
    contacts_list = [PROFILES[uid] for uid in ids if uid in PROFILES]
    return jsonify(contacts_list)

@app.route('/profile/<user_id>', methods=['POST'])
def update_user_profile(user_id):
    if user_id not in PROFILES:
        return jsonify({'error': 'User not found'}), 404
    profile = PROFILES[user_id]
    # Update text fields
    for field in ['bio_long', 'looking_for', 'offering', 'telegram']:
        if field in request.form:
            profile[field] = request.form.get(field)
    # Roles and main role
    roles = request.form.getlist('roles')
    if roles:
        profile['roles'] = roles
    main_role = request.form.get('main_role')
    if main_role and main_role in profile.get('roles', []):
        r = profile['roles']
        r.insert(0, r.pop(r.index(main_role)))
        profile['roles'] = r
    # Avatar upload
    avatar = request.files.get('avatar')
    if avatar and avatar.filename:
        filename = secure_filename(avatar.filename)
        ext = os.path.splitext(filename)[1]
        new_name = f"{user_id}{ext}"
        save_path = os.path.join(app.static_folder, 'assets', new_name)
        avatar.save(save_path)
        profile['avatarUrl'] = f"/assets/{new_name}"
    return jsonify({'status': 'ok', 'profile': profile})

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000)
