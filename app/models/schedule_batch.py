from app import db
from datetime import datetime
import uuid


class ScheduleBatch(db.Model):
    """Groups schedule entries with draft/published status"""
    __tablename__ = 'schedule_batches'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    semester = db.Column(db.String(10), nullable=False)  # WINTER, SUMMER
    group_id = db.Column(db.String(25), db.ForeignKey('student_groups.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='DRAFT')  # DRAFT, PUBLISHED
    
    # Optimization metrics
    preference_score = db.Column(db.Float, default=0.0)  # % of preferences satisfied
    teacher_gaps = db.Column(db.Integer, default=0)  # Number of gaps for teachers
    student_gaps = db.Column(db.Integer, default=0)  # Number of gaps for students
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group = db.relationship('StudentGroup', backref='schedule_batches')
    entries = db.relationship('ScheduleEntry', back_populates='batch', cascade='all, delete-orphan')
    
    def to_dict(self, include_entries=False):
        data = {
            'id': self.id,
            'semester': self.semester,
            'groupId': self.group_id,
            'groupName': self.group.name if self.group else None,
            'status': self.status,
            'preferenceScore': self.preference_score,
            'teacherGaps': self.teacher_gaps,
            'studentGaps': self.student_gaps,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'publishedAt': self.published_at.isoformat() if self.published_at else None,
            'entriesCount': len(self.entries) if self.entries else 0
        }
        if include_entries:
            data['entries'] = [e.to_dict() for e in self.entries]
        return data
