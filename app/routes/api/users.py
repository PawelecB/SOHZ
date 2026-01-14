from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.student_group import StudentGroup

bp = Blueprint('users_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict(include_group=True) for u in users])


@bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    user = User(
        id=User.generate_id(),
        email=data.get('email'),
        name=data.get('name'),
        role=data.get('role', 'STUDENT'),
        group_id=data.get('groupId') or None
    )
    user.set_password(data.get('password', 'password123'))
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict(include_group=True)), 201


@bp.route('/users/<id>', methods=['GET'])
@login_required
@admin_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'Nie znaleziono użytkownika'}), 404
    return jsonify(user.to_dict(include_group=True))


@bp.route('/users/<id>', methods=['PUT'])
@login_required
@admin_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'Nie znaleziono użytkownika'}), 404
    
    data = request.get_json()
    
    if data.get('email'):
        user.email = data['email']
    if data.get('name'):
        user.name = data['name']
    if data.get('role'):
        user.role = data['role']
    if 'groupId' in data:
        user.group_id = data['groupId'] or None
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict(include_group=True))


@bp.route('/users/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'Nie znaleziono użytkownika'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})
