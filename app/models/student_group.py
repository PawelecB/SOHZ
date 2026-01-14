from app import db
from datetime import datetime
import uuid


class StudentGroup(db.Model):
    __tablename__ = 'student_groups'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('User', back_populates='group')
    teacher_subjects = db.relationship('TeacherSubject', back_populates='group', cascade='all, delete-orphan')
    schedule_entries = db.relationship('ScheduleEntry', back_populates='group', cascade='all, delete-orphan')
    
    @property
    def size(self):
        """Calculate group size from students count"""
        return len(self.students) if self.students else 0
    
    def to_dict(self, include_count=False):
        data = {
            'id': self.id,
            'name': self.name,
            'size': self.size  # calculated from students
        }
        if include_count:
            data['_count'] = {'students': self.size}
        return data
