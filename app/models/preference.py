from app import db
from datetime import datetime
import uuid


class Preference(db.Model):
    __tablename__ = 'preferences'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    teacher_id = db.Column(db.String(25), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    teacher_subject_id = db.Column(db.String(25), db.ForeignKey('teacher_subjects.id', ondelete='CASCADE'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 4 = Friday
    time_slot = db.Column(db.Integer, nullable=False)  # 1-7
    priority = db.Column(db.Integer, default=1)  # 1 = low, 3 = high
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', back_populates='preferences')
    teacher_subject = db.relationship('TeacherSubject', back_populates='preferences')
    
    def to_dict(self):
        return {
            'id': self.id,
            'teacherId': self.teacher_id,
            'teacherSubjectId': self.teacher_subject_id,
            'dayOfWeek': self.day_of_week,
            'timeSlot': self.time_slot,
            'priority': self.priority
        }
