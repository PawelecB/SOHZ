from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.schedule_entry import ScheduleEntry
from app.models.schedule_batch import ScheduleBatch
from app.models.student_group import StudentGroup
from app.models.teacher_subject import TeacherSubject
from app.models.room import Room
from app.models.preference import Preference
from app.services.schedule_generator import generate_schedule, publish_batches, reoptimize_drafts

bp = Blueprint('schedule_api', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'ADMIN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/schedule', methods=['GET'])
@login_required
def get_schedule():
    semester = request.args.get('semester', 'WINTER')
    
    # Base query with batch join
    query = ScheduleEntry.query.join(ScheduleBatch)
    
    # Non-admin users only see PUBLISHED schedules
    if current_user.role != 'ADMIN':
        query = query.filter(ScheduleBatch.status == 'PUBLISHED')
    
    if current_user.role == 'STUDENT' and current_user.group_id:
        entries = query.filter(
            ScheduleEntry.group_id == current_user.group_id,
            ScheduleEntry.semester == semester
        ).order_by(ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot).all()
    elif current_user.role == 'TEACHER':
        teacher_subject_ids = [ts.id for ts in current_user.teacher_subjects]
        entries = query.filter(
            ScheduleEntry.teacher_subject_id.in_(teacher_subject_ids),
            ScheduleEntry.semester == semester
        ).order_by(ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot).all()
    else:
        # Admin sees all
        entries = ScheduleEntry.query.join(ScheduleBatch).filter(
            ScheduleBatch.status == 'PUBLISHED',
            ScheduleEntry.semester == semester
        ).order_by(
            ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot
        ).all()
    
    return jsonify([e.to_dict() for e in entries])


@bp.route('/schedule/group/<id>', methods=['GET'])
@login_required
def get_schedule_for_group(id):
    semester = request.args.get('semester', 'WINTER')
    
    query = ScheduleEntry.query.join(ScheduleBatch).filter(
        ScheduleEntry.group_id == id,
        ScheduleEntry.semester == semester
    )
    
    # Non-admin only sees published
    if current_user.role != 'ADMIN':
        query = query.filter(ScheduleBatch.status == 'PUBLISHED')
    
    entries = query.order_by(
        ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot
    ).all()
    
    return jsonify([e.to_dict() for e in entries])


@bp.route('/schedule/teacher/<id>', methods=['GET'])
@login_required
def get_schedule_for_teacher(id):
    semester = request.args.get('semester', 'WINTER')
    
    teacher_subjects = TeacherSubject.query.filter_by(teacher_id=id).all()
    teacher_subject_ids = [ts.id for ts in teacher_subjects]
    
    query = ScheduleEntry.query.join(ScheduleBatch).filter(
        ScheduleEntry.teacher_subject_id.in_(teacher_subject_ids),
        ScheduleEntry.semester == semester
    )
    
    # Non-admin only sees published
    if current_user.role != 'ADMIN':
        query = query.filter(ScheduleBatch.status == 'PUBLISHED')
    
    entries = query.order_by(
        ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot
    ).all()
    
    return jsonify([e.to_dict() for e in entries])


# ===== DRAFT MANAGEMENT ENDPOINTS (Admin only) =====

@bp.route('/schedule/drafts', methods=['GET'])
@login_required
@admin_required
def get_draft_batches():
    """Get all draft schedule batches"""
    semester = request.args.get('semester', 'WINTER')
    
    batches = ScheduleBatch.query.filter_by(
        semester=semester,
        status='DRAFT'
    ).order_by(ScheduleBatch.created_at.desc()).all()
    
    return jsonify([b.to_dict() for b in batches])


@bp.route('/schedule/batches', methods=['GET'])
@login_required
@admin_required
def get_all_batches():
    """Get all schedule batches (draft + published)"""
    semester = request.args.get('semester', 'WINTER')
    
    batches = ScheduleBatch.query.filter_by(
        semester=semester
    ).order_by(ScheduleBatch.created_at.desc()).all()
    
    return jsonify([b.to_dict() for b in batches])


@bp.route('/schedule/generate', methods=['POST'])
@login_required
@admin_required
def generate_schedule_endpoint():
    """Generate a new schedule (creates DRAFT)"""
    data = request.get_json()
    
    if not data or not data.get('groupId'):
        return jsonify({'error': 'Group ID is required'}), 400
    
    group_id = data.get('groupId')
    semester = data.get('semester', 'WINTER')
    resolved_conflicts = data.get('resolvedConflicts', {})
    
    result = generate_schedule(group_id, semester, resolved_conflicts)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/schedule/publish', methods=['POST'])
@login_required
@admin_required
def publish_schedules():
    """Publish selected draft schedules"""
    data = request.get_json()
    
    if not data or not data.get('batchIds'):
        return jsonify({'error': 'Batch IDs are required'}), 400
    
    batch_ids = data.get('batchIds')
    result = publish_batches(batch_ids)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/schedule/reoptimize', methods=['POST'])
@login_required
@admin_required
def reoptimize_schedules():
    """Re-optimize selected draft schedules"""
    data = request.get_json()
    
    if not data or not data.get('batchIds'):
        return jsonify({'error': 'Batch IDs are required'}), 400
    
    batch_ids = data.get('batchIds')
    semester = data.get('semester', 'WINTER')
    weights = data.get('weights')
    
    result = reoptimize_drafts(batch_ids, semester, weights)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@bp.route('/schedule/batch/<id>', methods=['DELETE'])
@login_required
@admin_required
def delete_batch(id):
    """Delete a draft schedule batch"""
    batch = ScheduleBatch.query.get(id)
    
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    if batch.status == 'PUBLISHED':
        return jsonify({'error': 'Cannot delete published schedule'}), 400
    
    db.session.delete(batch)
    db.session.commit()
    
    return jsonify({'success': True})
