from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            error = 'Nieprawidłowy email lub hasło'
    
    return render_template('login.html', error=error)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/api/auth/login', methods=['POST'])
def api_login():
    from flask import jsonify
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Brak danych'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'groupId': user.group_id,
                'groupName': user.group.name if user.group else None
            }
        })
    
    return jsonify({'error': 'Nieprawidłowy email lub hasło'}), 401


@bp.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    from flask import jsonify
    logout_user()
    return jsonify({'success': True})


@bp.route('/api/auth/session')
def api_session():
    from flask import jsonify
    if current_user.is_authenticated:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'role': current_user.role,
                'groupId': current_user.group_id,
                'groupName': current_user.group.name if current_user.group else None
            }
        })
    return jsonify({'user': None})
