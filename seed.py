"""
Seed script to populate database with sample data
Port from prisma/seed.ts
"""

from app import create_app, db
from app.models.user import User
from app.models.room import Room
from app.models.subject import Subject
from app.models.student_group import StudentGroup
from app.models.teacher_subject import TeacherSubject
from app.models.preference import Preference
import uuid

def generate_id():
    return str(uuid.uuid4())[:25]

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Create instance directory if it doesn't exist
        import os
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        
        # Create all database tables
        db.create_all()
        print("Database tables created.")
        
        # Clear existing data
        TeacherSubject.query.delete()
        Preference.query.delete()
        User.query.delete()
        Room.query.delete()
        Subject.query.delete()
        StudentGroup.query.delete()
        db.session.commit()
        
        print("Creating groups...")
        groups = []
        group_names = ['INF-1A', 'INF-1B', 'INF-2A', 'INF-2B', 'INF-3A']
        for name in group_names:
            group = StudentGroup(id=generate_id(), name=name)
            groups.append(group)
            db.session.add(group)
        db.session.commit()
        
        print("Creating rooms...")
        rooms_data = [
            ('Aula A1', 'LECTURE', 200),
            ('Aula A2', 'LECTURE', 150),
            ('Sala 101', 'LECTURE', 60),
            ('Sala 102', 'LECTURE', 60),
            ('Sala 103', 'LECTURE', 45),
            ('Lab 1', 'LAB', 30),
            ('Lab 2', 'LAB', 30),
            ('Lab 3', 'LAB', 25),
            ('Lab 4', 'LAB', 25),
        ]
        for name, rtype, cap in rooms_data:
            room = Room(id=generate_id(), name=name, type=rtype, capacity=cap)
            db.session.add(room)
        db.session.commit()
        
        print("Creating subjects...")
        subjects_data = [
            ('Matematyka', 'LECTURE', 30),
            ('Fizyka', 'LECTURE', 30),
            ('Programowanie', 'LAB', 30),
            ('Algorytmy', 'LECTURE', 30),
            ('Bazy danych', 'LAB', 15),
            ('Sieci komputerowe', 'LAB', 15),
            ('Systemy operacyjne', 'LECTURE', 30),
            ('Inżynieria oprogramowania', 'LECTURE', 15),
        ]
        subjects = []
        for name, stype, hours in subjects_data:
            subject = Subject(id=generate_id(), name=name, type=stype, hours_per_semester=hours)
            subjects.append(subject)
            db.session.add(subject)
        db.session.commit()
        
        print("Creating users...")
        # Admin
        admin = User(id=generate_id(), email='admin@uczelnia.pl', name='Administrator Systemu', role='ADMIN')
        admin.set_password('password123')
        db.session.add(admin)
        
        # Teachers
        teachers_data = [
            ('Jan Nowak', 'jan.nowak@uczelnia.pl'),
            ('Anna Kowalska', 'anna.kowalska@uczelnia.pl'),
            ('Piotr Wiśniewski', 'piotr.wisniewski@uczelnia.pl'),
            ('Maria Dąbrowska', 'maria.dabrowska@uczelnia.pl'),
        ]
        teachers = []
        for name, email in teachers_data:
            teacher = User(id=generate_id(), email=email, name=name, role='TEACHER')
            teacher.set_password('password123')
            teachers.append(teacher)
            db.session.add(teacher)
        
        # Students
        for i, group in enumerate(groups):
            for j in range(5):
                student = User(
                    id=generate_id(),
                    email=f'student{i*5+j+1}@uczelnia.pl',
                    name=f'Student {i*5+j+1}',
                    role='STUDENT',
                    group_id=group.id
                )
                student.set_password('password123')
                db.session.add(student)
        db.session.commit()
        
        print("Creating teacher-subject assignments...")
        # Assign teachers to subjects and groups
        assignments = [
            (0, 0, 0),  # Jan Nowak -> Matematyka -> INF-1A
            (0, 0, 1),  # Jan Nowak -> Matematyka -> INF-1B
            (0, 3, 0),  # Jan Nowak -> Algorytmy -> INF-1A
            (1, 1, 0),  # Anna Kowalska -> Fizyka -> INF-1A
            (1, 1, 1),  # Anna Kowalska -> Fizyka -> INF-1B
            (2, 2, 0),  # Piotr Wiśniewski -> Programowanie -> INF-1A
            (2, 2, 1),  # Piotr Wiśniewski -> Programowanie -> INF-1B
            (2, 4, 0),  # Piotr Wiśniewski -> Bazy danych -> INF-1A
            (3, 5, 0),  # Maria Dąbrowska -> Sieci -> INF-1A
            (3, 6, 0),  # Maria Dąbrowska -> Systemy operacyjne -> INF-1A
        ]
        for ti, si, gi in assignments:
            ts = TeacherSubject(
                id=generate_id(),
                teacher_id=teachers[ti].id,
                subject_id=subjects[si].id,
                group_id=groups[gi].id
            )
            db.session.add(ts)
        db.session.commit()
        
        print("Creating teacher preferences...")
        # Jan Nowak prefers mornings
        for day in range(5):
            for slot in [1, 2, 3]:
                pref = Preference(id=generate_id(), teacher_id=teachers[0].id, day_of_week=day, time_slot=slot, priority=3)
                db.session.add(pref)
        
        # Anna Kowalska prefers afternoons
        for day in range(5):
            for slot in [4, 5, 6]:
                pref = Preference(id=generate_id(), teacher_id=teachers[1].id, day_of_week=day, time_slot=slot, priority=2)
                db.session.add(pref)
        
        db.session.commit()
        
        print("Seed completed successfully!")
        print("\nTest accounts:")
        print("| Role               | Email                    | Password    |")
        print("|-------------------|--------------------------|-------------|")
        print("| Dziekanat (Admin) | admin@uczelnia.pl        | password123 |")
        print("| Pracownik         | jan.nowak@uczelnia.pl    | password123 |")
        print("| Student           | student1@uczelnia.pl     | password123 |")

if __name__ == '__main__':
    seed_database()
