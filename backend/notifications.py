#!/usr/bin/env python3
"""
Notifications module: maintain ActivityLog and emit WebSocket notifications.
"""
import uuid
from datetime import datetime

# WebSocket instance to be set by app
socketio = None

# In-memory activity log store: list of dicts
activity_logs = []

def init_app(sio):
    """
    Initialize the notifications module with the SocketIO instance.
    """
    global socketio
    socketio = sio

def log_event(user_id, event_type, details=None):
    """
    Create an ActivityLog entry and emit a 'notification' event to the user room.
    details: arbitrary dict of event details.
    Returns the event dict.
    """
    event = {
        'event_id': str(uuid.uuid4()),
        'user_id': user_id,
        'type': event_type,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    activity_logs.append(event)
    # Emit via WebSocket
    if socketio:
        payload = {
            'type': event_type,
            'message': event['details'].get('message', ''),
            'payload': event
        }
        socketio.emit('notification', payload, room=user_id)
    return event

def get_logs(user_id):
    """
    Retrieve all ActivityLog entries for a given user_id.
    """
    return [e for e in activity_logs if e.get('user_id') == user_id]

def broadcast_graph_update(update_type, data):
    """
    Emit a 'graph_update' event to all connected clients.
    update_type: 'new_node'|'new_link'|'update_link'
    data: payload dict.
    """
    if socketio:
        payload = {'type': update_type, 'data': data}
        socketio.emit('graph_update', payload)
