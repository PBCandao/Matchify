#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_socketio import SocketIO

import models

import graph_logic
import contacts
import recommendations
import notifications

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
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

# WebSocket notifications are emitted via notifications module

if __name__ == '__main__':
    # ─── TEMPORARY TEST DATA ───
    # so our /graph endpoint returns something immediately
    from graph_logic import add_user, add_relationship

    add_user('alice', name='Alice', roles=['Developer'], phoneHash='hash1')
    add_user('bob', name='Bob', roles=['Investor'], phoneHash='hash2')
    add_relationship('alice', 'bob', weight=1.0, status='connected')
    # ─────────────────────────────

    socketio.run(app, host='0.0.0.0', port=5000)
