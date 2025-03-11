from flask import session
from ..database import db
from datetime import datetime
from flask_socketio import SocketIO
from AdminDashboard.routes.models import Message, User
from flask_socketio import emit, join_room, leave_room

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    user_id = session.get('user_id')
    user = db.session.query(User).get(user_id)    
    if user:        
        if session.get('room_id') != room:
            session['room_id'] = room  
            join_room(room)
            messages = db.session.query(Message).filter_by(room_id=room).all()
            for message in messages:
                emit('message', {'msg': message.content, 'name': message.user.name, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, room=room)
            emit('message', {'msg': f'{user.name} has joined the room.', 'name': 'System', 'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}, room=room)
        else:
            pass  
    else:
        print("Error: User is not found!")

@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    room_id = session.get('room_id')
    user_id = session.get('user_id')
    user = db.session.query(User).get(user_id)
    if user and room_id:
        message = Message(content=msg, user=user, room_id=room_id)
        db.session.add(message)
        db.session.commit()
        emit('message', {'msg': msg, 'name': user.name, 'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}, room=room_id)
    else:
        print("Error: User or Room not found!")

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f'User left room {room}'}, room=room)