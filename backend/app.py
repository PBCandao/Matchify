#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_socketio import SocketIO

import models

import graph_logic
import contacts
import recommendations
import notifications

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
 
# Seed initial test data
graph_logic.add_user('alice', name='Alice', roles=['Developer'], phoneHash='h1')
graph_logic.add_user('bob', name='Bob', roles=['Investor'], phoneHash='h2')
graph_logic.add_relationship('alice', 'bob', weight=2.5, status='connected')

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
# Mock profile data
PROFILES = {
    'alice': {
        'id': 'alice',
        'name': 'Alice Smith',
        'roles': ['Developer'],
        'bio': 'Software developer with a passion for building social apps.',
        'lookingFor': 'Mentors in cybersecurity.',
        'offering': 'Insights into modern web development.',
        'avatarUrl': 'https://via.placeholder.com/150?text=AS'
    },
    'bob': {
        'id': 'bob',
        'name': 'Bob Johnson',
        'roles': ['Investor'],
        'bio': 'Seasoned investor focusing on tech startups.',
        'lookingFor': 'Rising entrepreneurs to support.',
        'offering': 'Funding and mentorship.',
        'avatarUrl': 'https://via.placeholder.com/150?text=BJ'
    },
    'charlie': {
        'id': 'charlie',
        'name': 'Charlie Brown',
        'roles': ['Designer'],
        'bio': 'Creative designer specializing in UX/UI.',
        'lookingFor': 'Collaborations on mobile apps.',
        'offering': 'Design consultations.',
        'avatarUrl': 'https://via.placeholder.com/150?text=CB'
    },
    'dana': {
        'id': 'dana',
        'name': 'Dana Scully',
        'roles': ['Analyst', 'Researcher'],
        'bio': 'Data analyst with a keen eye for insights.',
        'lookingFor': 'Challenging research projects.',
        'offering': 'In-depth analytics and reports.',
        'avatarUrl': 'https://via.placeholder.com/150?text=DS'
    },
    'me': {
        'id': 'me',
        'name': 'My Name',
        'roles': ['Developer', 'Mentor'],
        'bio': 'This is my profile summary.',
        'lookingFor': 'Networking opportunities.',
        'offering': 'Guidance to new developers.',
        'avatarUrl': 'https://via.placeholder.com/150?text=ME'
    }
}

@app.route('/profile/me')
def get_my_profile():
    return jsonify(PROFILES.get('me', {}))

@app.route('/profile/<user_id>')
def get_user_profile(user_id):
    profile = PROFILES.get(user_id)
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(profile)

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000)
