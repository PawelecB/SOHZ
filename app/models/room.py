from app import db
from datetime import datetime
import uuid


class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.String(25), primary_key=True, default=lambda: str(uuid.uuid4())[:25])
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # LECTURE, LAB
    capacity = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedule_entries = db.relationship('ScheduleEntry', back_populates='room', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'capacity': self.capacity
        }
