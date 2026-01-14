from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.student_group import StudentGroup

bp = Blueprint('groups_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/groups', methods=['GET'])
@login_required
def get_groups():
    groups = StudentGroup.query.all()
    return jsonify([g.to_dict(include_count=True) for g in groups])


@bp.route('/groups', methods=['POST'])
@login_required
@admin_required
def create_group():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    group = StudentGroup(
        name=data.get('name')
    )
    
    db.session.add(group)
    db.session.commit()
    
    return jsonify(group.to_dict(include_count=True)), 201


@bp.route('/groups/<id>', methods=['GET'])
@login_required
def get_group(id):
    group = StudentGroup.query.get(id)
    if not group:
        return jsonify({'error': 'Nie znaleziono grupy'}), 404
    return jsonify(group.to_dict(include_count=True))


@bp.route('/groups/<id>', methods=['PUT'])
@login_required
@admin_required
def update_group(id):
    group = StudentGroup.query.get(id)
    if not group:
        return jsonify({'error': 'Nie znaleziono grupy'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        group.name = data['name']
    
    db.session.commit()
    return jsonify(group.to_dict(include_count=True))


@bp.route('/groups/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_group(id):
    group = StudentGroup.query.get(id)
    if not group:
        return jsonify({'error': 'Nie znaleziono grupy'}), 404
    
    db.session.delete(group)
    db.session.commit()
    return jsonify({'success': True})
