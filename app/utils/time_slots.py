# Time slots configuration for the schedule system
# Each block is 1.5 hours (90 minutes) with 15-minute breaks between blocks

TIME_SLOTS = [
    {'slot': 1, 'startTime': '08:00', 'endTime': '09:30', 'label': '8:00 - 9:30'},
    {'slot': 2, 'startTime': '09:45', 'endTime': '11:15', 'label': '9:45 - 11:15'},
    {'slot': 3, 'startTime': '11:30', 'endTime': '13:00', 'label': '11:30 - 13:00'},
    {'slot': 4, 'startTime': '13:15', 'endTime': '14:45', 'label': '13:15 - 14:45'},
    {'slot': 5, 'startTime': '15:00', 'endTime': '16:30', 'label': '15:00 - 16:30'},
    {'slot': 6, 'startTime': '16:45', 'endTime': '18:15', 'label': '16:45 - 18:15'},
    {'slot': 7, 'startTime': '18:30', 'endTime': '20:00', 'label': '18:30 - 20:00'},
]

DAYS = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
DAYS_SHORT = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt']


def get_slot_label(slot):
    for s in TIME_SLOTS:
        if s['slot'] == slot:
            return s['label']
    return f'Blok {slot}'


def get_slot_by_number(slot):
    for s in TIME_SLOTS:
        if s['slot'] == slot:
            return s
    return None
