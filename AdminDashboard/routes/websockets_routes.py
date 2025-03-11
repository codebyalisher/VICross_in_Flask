from ..database import db
from AdminDashboard.routes.models import Room,User
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template

bp = Blueprint('sockets', __name__, url_prefix='/sockets')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']
        user =db.session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('sockets.index'))
    return render_template('login.html')

@bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('sockets.login'))
    rooms = db.session.query(Room).all()
    return render_template('chat.html',rooms=rooms)

@bp.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'POST':
        name = request.form['name']
        room = Room(name=name)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('sockets.rooms'))
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)

@bp.route('/join_room/<int:room_id>')
def join_room(room_id):
    if room_id is not None:
        session['room_id'] = room_id
        return redirect(url_for('sockets.index'))
    else:
        logging.error("Invalid room_id provided.")
        return redirect(url_for('sockets.index'))

@bp.route('/leave_room')
def leave_room():
    session.pop('room_id', None)
    return redirect(url_for('sockets.index'))

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('sockets.login'))