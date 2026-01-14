from app import db
from datetime import datetime
import uuid


class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # LECTURE, LAB
    hours_per_semester = db.Column(db.Integer, default=30)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', back_populates='subject', cascade='all, delete-orphan')
    schedule_entries = db.relationship('ScheduleEntry', back_populates='subject', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'hoursPerSemester': self.hours_per_semester
        }
