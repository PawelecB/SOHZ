from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.subject import Subject

bp = Blueprint('subjects_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects])


@bp.route('/subjects', methods=['POST'])
@login_required
@admin_required
def create_subject():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    subject = Subject(
        name=data.get('name'),
        type=data.get('type', 'LECTURE'),
        hours_per_semester=int(data.get('hoursPerSemester', 30))
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(subject.to_dict()), 201


@bp.route('/subjects/<id>', methods=['GET'])
@login_required
def get_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        return jsonify({'error': 'Nie znaleziono przedmiotu'}), 404
    return jsonify(subject.to_dict())


@bp.route('/subjects/<id>', methods=['PUT'])
@login_required
@admin_required
def update_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        return jsonify({'error': 'Nie znaleziono przedmiotu'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        subject.name = data['name']
    if data.get('type'):
        subject.type = data['type']
    if data.get('hoursPerSemester'):
        subject.hours_per_semester = int(data['hoursPerSemester'])
    
    db.session.commit()
    return jsonify(subject.to_dict())


@bp.route('/subjects/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        return jsonify({'error': 'Nie znaleziono przedmiotu'}), 404
    
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'success': True})
