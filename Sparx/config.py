import os

class Config:
    """Konfiguracja aplikacji"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///schedule_optimizer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stałe aplikacji
    DAYS_OF_WEEK = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
    WORKING_HOURS = list(range(8, 20))  # 8:00 - 19:00
    LESSON_DURATION = 1.5  # godziny
    ROOM_TYPES = ['Wykładowa', 'Laboratoryjna', 'Seminarium']
    SUBJECT_TYPES = ['Wykład', 'Laboratorium', 'Ćwiczenia', 'Seminarium']
