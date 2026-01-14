from app import db
from datetime import datetime
import uuid


class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entries'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    batch_id = db.Column(db.String(25), db.ForeignKey('schedule_batches.id', ondelete='CASCADE'), nullable=True)
    semester = db.Column(db.String(10), nullable=False)  # WINTER, SUMMER
    week_number = db.Column(db.Integer, nullable=False)  # 1-15
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, 4 = Friday
    time_slot = db.Column(db.Integer, nullable=False)  # 1-7
    
    room_id = db.Column(db.String(25), db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    teacher_subject_id = db.Column(db.String(25), db.ForeignKey('teacher_subjects.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.String(25), db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    group_id = db.Column(db.String(25), db.ForeignKey('student_groups.id', ondelete='CASCADE'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraints - now per batch
    __table_args__ = (
        db.UniqueConstraint('batch_id', 'week_number', 'day_of_week', 'time_slot', 'room_id', 
                           name='unique_room_slot'),
        db.UniqueConstraint('batch_id', 'week_number', 'day_of_week', 'time_slot', 'teacher_subject_id', 
                           name='unique_teacher_slot'),
        db.UniqueConstraint('batch_id', 'week_number', 'day_of_week', 'time_slot', 'group_id', 
                           name='unique_group_slot'),
    )
    
    # Relationships
    batch = db.relationship('ScheduleBatch', back_populates='entries')
    room = db.relationship('Room', back_populates='schedule_entries')
    teacher_subject = db.relationship('TeacherSubject', back_populates='schedule_entries')
    subject = db.relationship('Subject', back_populates='schedule_entries')
    group = db.relationship('StudentGroup', back_populates='schedule_entries')
    
    @property
    def is_published(self):
        """Check if entry is published via batch status"""
        return self.batch.status == 'PUBLISHED' if self.batch else False
    
    def to_dict(self, include_relations=True):
        data = {
            'id': self.id,
            'batchId': self.batch_id,
            'semester': self.semester,
            'weekNumber': self.week_number,
            'dayOfWeek': self.day_of_week,
            'timeSlot': self.time_slot,
            'isPublished': self.is_published
        }
        if include_relations:
            data['room'] = {'name': self.room.name, 'type': self.room.type}
            data['subject'] = {'name': self.subject.name, 'type': self.subject.type}
            data['group'] = {'id': self.group.id, 'name': self.group.name}
            data['teacherSubject'] = {
                'teacher': {'name': self.teacher_subject.teacher.name}
            }
        return data

