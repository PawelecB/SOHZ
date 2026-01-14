from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.teacher_subject import TeacherSubject

bp = Blueprint('assignments_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/assignments', methods=['GET'])
@login_required
def get_assignments():
    assignments = TeacherSubject.query.all()
    return jsonify([a.to_dict(include_relations=True) for a in assignments])


@bp.route('/assignments', methods=['POST'])
@login_required
@admin_required
def create_assignment():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    assignment = TeacherSubject(
        teacher_id=data.get('teacherId'),
        subject_id=data.get('subjectId'),
        group_id=data.get('groupId')
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify(assignment.to_dict(include_relations=True)), 201


@bp.route('/assignments/<id>', methods=['GET'])
@login_required
def get_assignment(id):
    assignment = TeacherSubject.query.get(id)
    if not assignment:
        return jsonify({'error': 'Nie znaleziono przypisania'}), 404
    return jsonify(assignment.to_dict(include_relations=True))


@bp.route('/assignments/<id>', methods=['PUT'])
@login_required
@admin_required
def update_assignment(id):
    assignment = TeacherSubject.query.get(id)
    if not assignment:
        return jsonify({'error': 'Nie znaleziono przypisania'}), 404
    
    data = request.get_json()
    
    if data.get('teacherId'):
        assignment.teacher_id = data['teacherId']
    if data.get('subjectId'):
        assignment.subject_id = data['subjectId']
    if data.get('groupId'):
        assignment.group_id = data['groupId']
    
    db.session.commit()
    return jsonify(assignment.to_dict(include_relations=True))


@bp.route('/assignments/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_assignment(id):
    assignment = TeacherSubject.query.get(id)
    if not assignment:
        return jsonify({'error': 'Nie znaleziono przypisania'}), 404
    
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'success': True})
