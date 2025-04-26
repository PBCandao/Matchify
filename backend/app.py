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

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5000)
