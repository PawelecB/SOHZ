from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Dekorator wymuszający zalogowanie"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Musisz się zalogować', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Dekorator wymuszający wymaganą rolę"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Musisz się zalogować', 'danger')
                return redirect(url_for('login'))
            
            from models import User
            user = User.query.get(session['user_id'])
            if not user or user.role not in allowed_roles:
                flash('Brak dostępu do tej strony', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
