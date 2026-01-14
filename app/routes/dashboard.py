from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, Room, Subject, StudentGroup, ScheduleEntry

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@bp.route('/')
@login_required
def index():
    stats = None
    if current_user.role == 'ADMIN':
        stats = {
            'users': User.query.count(),
            'rooms': Room.query.count(),
            'subjects': Subject.query.count(),
            'groups': StudentGroup.query.count(),
            'scheduleEntries': ScheduleEntry.query.count()
        }
    return render_template('dashboard/index.html', stats=stats)


@bp.route('/users')
@login_required
@role_required('ADMIN')
def users():
    return render_template('dashboard/users.html')


@bp.route('/rooms')
@login_required
@role_required('ADMIN')
def rooms():
    return render_template('dashboard/rooms.html')


@bp.route('/subjects')
@login_required
@role_required('ADMIN')
def subjects():
    return render_template('dashboard/subjects.html')


@bp.route('/groups')
@login_required
@role_required('ADMIN')
def groups():
    return render_template('dashboard/groups.html')


@bp.route('/assignments')
@login_required
@role_required('ADMIN')
def assignments():
    return render_template('dashboard/assignments.html')


@bp.route('/generate')
@login_required
@role_required('ADMIN')
def generate():
    return render_template('dashboard/generate.html')


@bp.route('/schedule')
@login_required
def schedule():
    return render_template('dashboard/schedule.html')


@bp.route('/preferences')
@login_required
@role_required('TEACHER')
def preferences():
    return render_template('dashboard/preferences.html')


@bp.route('/teachers')
@login_required
@role_required('STUDENT')
def teachers():
    return render_template('dashboard/teachers.html')


@bp.route('/students')
@login_required
@role_required('ADMIN')
def students():
    return render_template('dashboard/students.html')
