from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.preference import Preference

bp = Blueprint('preferences_api', __name__)


@bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    if current_user.role == 'ADMIN':
        preferences = Preference.query.all()
    else:
        preferences = Preference.query.filter_by(teacher_id=current_user.id).all()
    return jsonify([p.to_dict() for p in preferences])


@bp.route('/preferences', methods=['POST'])
@login_required
def create_preference():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    # Teachers can only create their own preferences
    teacher_id = current_user.id if current_user.role == 'TEACHER' else data.get('teacherId', current_user.id)
    
    preference = Preference(
        teacher_id=teacher_id,
        teacher_subject_id=data.get('teacherSubjectId'),
        day_of_week=int(data.get('dayOfWeek', 0)),
        time_slot=int(data.get('timeSlot', 1)),
        priority=int(data.get('priority', 1))
    )
    
    db.session.add(preference)
    db.session.commit()
    
    return jsonify(preference.to_dict()), 201


@bp.route('/preferences/<id>', methods=['GET'])
@login_required
def get_preference(id):
    preference = Preference.query.get(id)
    if not preference:
        return jsonify({'error': 'Nie znaleziono preferencji'}), 404
    
    # Teachers can only view their own preferences
    if current_user.role == 'TEACHER' and preference.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(preference.to_dict())


@bp.route('/preferences/<id>', methods=['PUT'])
@login_required
def update_preference(id):
    preference = Preference.query.get(id)
    if not preference:
        return jsonify({'error': 'Nie znaleziono preferencji'}), 404
    
    # Teachers can only update their own preferences
    if current_user.role == 'TEACHER' and preference.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if 'dayOfWeek' in data:
        preference.day_of_week = int(data['dayOfWeek'])
    if 'timeSlot' in data:
        preference.time_slot = int(data['timeSlot'])
    if 'priority' in data:
        preference.priority = int(data['priority'])
    
    db.session.commit()
    return jsonify(preference.to_dict())


@bp.route('/preferences/<id>', methods=['DELETE'])
@login_required
def delete_preference(id):
    preference = Preference.query.get(id)
    if not preference:
        return jsonify({'error': 'Nie znaleziono preferencji'}), 404
    
    # Teachers can only delete their own preferences
    if current_user.role == 'TEACHER' and preference.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    db.session.delete(preference)
    db.session.commit()
    return jsonify({'success': True})
