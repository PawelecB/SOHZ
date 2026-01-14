from app import db
from flask_login import UserMixin
import bcrypt
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(25), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='STUDENT')  # ADMIN, TEACHER, STUDENT
    group_id = db.Column(db.String(25), db.ForeignKey('student_groups.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group = db.relationship('StudentGroup', back_populates='students')
    teacher_subjects = db.relationship('TeacherSubject', back_populates='teacher', cascade='all, delete-orphan')
    preferences = db.relationship('Preference', back_populates='teacher', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self, include_group=False):
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role
        }
        if include_group and self.group:
            data['group'] = {'id': self.group.id, 'name': self.group.name}
        return data
    
    @staticmethod
    def generate_id():
        import uuid
        return str(uuid.uuid4())[:25]
