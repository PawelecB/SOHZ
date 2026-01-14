from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.user import User

bp = Blueprint('teachers_api', __name__)


@bp.route('/teachers', methods=['GET'])
@login_required
def get_teachers():
    teachers = User.query.filter_by(role='TEACHER').all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'email': t.email
    } for t in teachers])
