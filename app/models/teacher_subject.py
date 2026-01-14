from app import db
from datetime import datetime
import uuid


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    teacher_id = db.Column(db.String(25), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.String(25), db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    group_id = db.Column(db.String(25), db.ForeignKey('student_groups.id', ondelete='CASCADE'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'subject_id', 'group_id', name='unique_teacher_subject_group'),
    )
    
    # Relationships
    teacher = db.relationship('User', back_populates='teacher_subjects')
    subject = db.relationship('Subject', back_populates='teacher_subjects')
    group = db.relationship('StudentGroup', back_populates='teacher_subjects')
    preferences = db.relationship('Preference', back_populates='teacher_subject', cascade='all, delete-orphan')
    schedule_entries = db.relationship('ScheduleEntry', back_populates='teacher_subject', cascade='all, delete-orphan')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'teacherId': self.teacher_id,
            'subjectId': self.subject_id,
            'groupId': self.group_id
        }
        if include_relations:
            data['teacher'] = {'id': self.teacher.id, 'name': self.teacher.name}
            data['subject'] = {'id': self.subject.id, 'name': self.subject.name, 'type': self.subject.type}
            data['group'] = {'id': self.group.id, 'name': self.group.name}
        return data
