from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.room import Room

bp = Blueprint('rooms_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/rooms', methods=['GET'])
@login_required
def get_rooms():
    rooms = Room.query.all()
    return jsonify([r.to_dict() for r in rooms])


@bp.route('/rooms', methods=['POST'])
@login_required
@admin_required
def create_room():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    room = Room(
        name=data.get('name'),
        type=data.get('type', 'LECTURE'),
        capacity=int(data.get('capacity', 30))
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify(room.to_dict()), 201


@bp.route('/rooms/<id>', methods=['GET'])
@login_required
def get_room(id):
    room = Room.query.get(id)
    if not room:
        return jsonify({'error': 'Nie znaleziono sali'}), 404
    return jsonify(room.to_dict())


@bp.route('/rooms/<id>', methods=['PUT'])
@login_required
@admin_required
def update_room(id):
    room = Room.query.get(id)
    if not room:
        return jsonify({'error': 'Nie znaleziono sali'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        room.name = data['name']
    if data.get('type'):
        room.type = data['type']
    if data.get('capacity'):
        room.capacity = int(data['capacity'])
    
    db.session.commit()
    return jsonify(room.to_dict())


@bp.route('/rooms/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_room(id):
    room = Room.query.get(id)
    if not room:
        return jsonify({'error': 'Nie znaleziono sali'}), 404
    
    db.session.delete(room)
    db.session.commit()
    return jsonify({'success': True})
