from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Zaloguj się, aby uzyskać dostęp do tej strony.'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main, auth, dashboard
    from app.routes.api import users, rooms, subjects, groups, assignments, preferences, schedule, teachers

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    
    # API blueprints
    app.register_blueprint(users.bp, url_prefix='/api')
    app.register_blueprint(rooms.bp, url_prefix='/api')
    app.register_blueprint(subjects.bp, url_prefix='/api')
    app.register_blueprint(groups.bp, url_prefix='/api')
    app.register_blueprint(assignments.bp, url_prefix='/api')
    app.register_blueprint(preferences.bp, url_prefix='/api')
    app.register_blueprint(schedule.bp, url_prefix='/api')
    app.register_blueprint(teachers.bp, url_prefix='/api')

    return app


from app.models import user

@login_manager.user_loader
def load_user(id):
    return user.User.query.get(id)
