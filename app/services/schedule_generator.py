"""
Schedule Generator - port from TypeScript
Enhanced with draft/publish workflow and optimization metrics
"""

from app import db
from app.models.teacher_subject import TeacherSubject
from app.models.room import Room
from app.models.preference import Preference
from app.models.student_group import StudentGroup
from app.models.schedule_batch import ScheduleBatch
from app.models.schedule_entry import ScheduleEntry
from datetime import datetime
import math

# Constants
WEEKS_PER_SEMESTER = 15
TIME_SLOTS = [1, 2, 3, 4, 5, 6, 7]  # 7 slots per day, each 1.5h
DAYS = [0, 1, 2, 3, 4]  # Mon-Fri


def get_current_semester():
    month = datetime.now().month
    if month >= 10 or month <= 2:
        return 'WINTER'
    if 3 <= month <= 7:
        return 'SUMMER'
    return 'WINTER'


def find_suitable_room(rooms, subject_type, required_capacity, occupied_rooms):
    """Find an available room matching requirements"""
    room_type = 'LAB' if subject_type == 'LAB' else 'LECTURE'
    for room in rooms:
        if room.type == room_type and room.capacity >= required_capacity and room.id not in occupied_rooms:
            return room
    return None


def get_preference_score(preferences, teacher_id, day, slot):
    """Get preference score for a time slot"""
    for pref in preferences:
        if pref.teacher_id == teacher_id and pref.day_of_week == day and pref.time_slot == slot:
            return pref.priority
    return 0


def calculate_gaps(entries, entity_type='teacher'):
    """Calculate number of gaps (empty slots between classes) for teachers or students"""
    total_gaps = 0
    
    if not entries:
        return total_gaps
    
    # Group entries by day and week
    entity_entries = {}
    for entry in entries:
        if entity_type == 'teacher':
            # Get teacher_id from teacher_subject
            ts = TeacherSubject.query.get(entry.teacher_subject_id)
            key = ts.teacher_id if ts else None
        else:
            key = entry.group_id
        
        if key is None:
            continue
            
        if key not in entity_entries:
            entity_entries[key] = {}
        
        day_key = f"{entry.week_number}-{entry.day_of_week}"
        if day_key not in entity_entries[key]:
            entity_entries[key][day_key] = []
        entity_entries[key][day_key].append(entry.time_slot)
    
    # Count gaps for each entity
    for entity_id, days in entity_entries.items():
        for day_key, slots in days.items():
            slots.sort()
            if len(slots) > 1:
                for i in range(len(slots) - 1):
                    gap = slots[i + 1] - slots[i] - 1
                    if gap > 0:
                        total_gaps += gap
    
    return total_gaps


def calculate_preference_score(entries, preferences):
    """Calculate percentage of entries matching teacher preferences"""
    if not entries:
        return 0.0
    
    matched = 0
    total = len(entries)
    
    for entry in entries:
        ts = TeacherSubject.query.get(entry.teacher_subject_id)
        if not ts:
            continue
        teacher_id = ts.teacher_id
        for pref in preferences:
            if (pref.teacher_id == teacher_id and 
                pref.day_of_week == entry.day_of_week and 
                pref.time_slot == entry.time_slot):
                matched += 1
                break
    
    return round((matched / total) * 100, 1) if total > 0 else 0.0


def generate_schedule(group_id, semester=None, resolved_conflicts=None, existing_batch_id=None, weights=None):
    """Generate schedule for a student group with weighted optimization"""
    if semester is None:
        semester = get_current_semester()
    
    if weights is None:
        weights = {'preferences': 2, 'teacher_gaps': 2, 'student_gaps': 2}
    
    if resolved_conflicts is None:
        resolved_conflicts = {}
    
    # Fetch data
    assignments = TeacherSubject.query.filter_by(group_id=group_id).all()
    rooms = Room.query.all()
    preferences = Preference.query.all()
    group = StudentGroup.query.get(group_id)
    
    if not group:
        return {'error': 'Group not found'}
    
    group_size = group.size if group.size > 0 else 1
    
    # Delete existing draft batch for this group and semester if exists
    if existing_batch_id:
        old_batch = ScheduleBatch.query.get(existing_batch_id)
        if old_batch:
            db.session.delete(old_batch)
            db.session.commit()
    else:
        # Delete any existing draft for this group/semester
        old_drafts = ScheduleBatch.query.filter_by(
            group_id=group_id, 
            semester=semester, 
            status='DRAFT'
        ).all()
        for old in old_drafts:
            db.session.delete(old)
        db.session.commit()
    
    # Create new batch in DRAFT status
    batch = ScheduleBatch(
        semester=semester,
        group_id=group_id,
        status='DRAFT'
    )
    db.session.add(batch)
    db.session.flush()  # Get the ID
    
    # Get existing PUBLISHED entries for occupancy calculation
    published_batches = ScheduleBatch.query.filter_by(semester=semester, status='PUBLISHED').all()
    published_entries = []
    for pb in published_batches:
        published_entries.extend(pb.entries)
    
    # Also consider other DRAFT batches for global optimization
    other_draft_batches = ScheduleBatch.query.filter(
        ScheduleBatch.semester == semester,
        ScheduleBatch.status == 'DRAFT',
        ScheduleBatch.group_id != group_id
    ).all()
    draft_entries = []
    for db_batch in other_draft_batches:
        draft_entries.extend(db_batch.entries)
    
    all_existing = published_entries + draft_entries
    
    schedule = []
    conflicts = []
    
    # Occupancy maps
    teacher_occupancy = {}
    group_occupancy = {}
    room_occupancy = {}
    
    # Build occupancy from existing entries
    for entry in all_existing:
        key = f"{entry.week_number}-{entry.day_of_week}-{entry.time_slot}"
        
        if entry.room_id not in room_occupancy:
            room_occupancy[entry.room_id] = set()
        room_occupancy[entry.room_id].add(key)
        
        if entry.teacher_subject.teacher_id not in teacher_occupancy:
            teacher_occupancy[entry.teacher_subject.teacher_id] = set()
        teacher_occupancy[entry.teacher_subject.teacher_id].add(key)
        
        if entry.group_id not in group_occupancy:
            group_occupancy[entry.group_id] = set()
        group_occupancy[entry.group_id].add(key)
    
    def is_slot_occupied(teacher_id, g_id, week, day, slot):
        key = f"{week}-{day}-{slot}"
        if teacher_id in teacher_occupancy and key in teacher_occupancy[teacher_id]:
            return True
        if g_id in group_occupancy and key in group_occupancy[g_id]:
            return True
        return False
    
    def mark_slot_occupied(teacher_id, g_id, room_id, week, day, slot):
        key = f"{week}-{day}-{slot}"
        if teacher_id not in teacher_occupancy:
            teacher_occupancy[teacher_id] = set()
        if g_id not in group_occupancy:
            group_occupancy[g_id] = set()
        if room_id not in room_occupancy:
            room_occupancy[room_id] = set()
        teacher_occupancy[teacher_id].add(key)
        group_occupancy[g_id].add(key)
        room_occupancy[room_id].add(key)
    
    def get_occupied_rooms_at_slot(week, day, slot):
        key = f"{week}-{day}-{slot}"
        occupied = set()
        for room_id, keys in room_occupancy.items():
            if key in keys:
                occupied.add(room_id)
        return occupied
    
    # Sort assignments by preference priority (higher first)
    def get_max_pref(assignment):
        max_pref = 0
        for p in preferences:
            if p.teacher_id == assignment.teacher_id:
                max_pref = max(max_pref, p.priority)
        return max_pref
    
    sorted_assignments = sorted(assignments, key=get_max_pref, reverse=True)
    
    # Process each assignment
    for assignment in sorted_assignments:
        slots_needed = math.ceil(assignment.subject.hours_per_semester / 1.5)
        slots_scheduled = 0
        
        # Apply resolved conflicts first
        resolved = resolved_conflicts.get(assignment.id, [])
        if resolved and isinstance(resolved, list):
            for sl in resolved:
                entry = ScheduleEntry(
                    batch_id=batch.id,
                    semester=semester,
                    week_number=sl.get('week'),
                    day_of_week=sl.get('day'),
                    time_slot=sl.get('slot') or sl.get('hour'),
                    room_id=sl.get('roomId'),
                    teacher_subject_id=assignment.id,
                    subject_id=assignment.subject_id,
                    group_id=assignment.group_id
                )
                schedule.append(entry)
                mark_slot_occupied(assignment.teacher_id, assignment.group_id, sl.get('roomId'),
                                 sl.get('week'), sl.get('day'), sl.get('slot') or sl.get('hour'))
                slots_scheduled += 1
        
        # Build weekly slot scores based on preferences
        weekly_slot_scores = []
        for day in DAYS:
            for slot in TIME_SLOTS:
                score = get_preference_score(preferences, assignment.teacher_id, day, slot) * 10
                score -= (slot - 1) * 0.1
                weekly_slot_scores.append({'day': day, 'slot': slot, 'score': score})
        
        weekly_slot_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate week interval
        slots_per_week = slots_needed / WEEKS_PER_SEMESTER
        week_interval = 1
        if slots_per_week < 1:
            week_interval = math.ceil(1 / slots_per_week)
        
        slot_index = 0
        week_offset = 0
        
        # Calculate distribution limits
        max_slots_per_week = math.ceil(slots_needed / WEEKS_PER_SEMESTER)
        # Ensure at least 1 slot per week allowed if weeks could be skipped due to interval
        if max_slots_per_week < 1: max_slots_per_week = 1
        
        # Strict daily limit for THIS SUBJECT (max 2 blocks of same subject per day)
        MAX_DAILY_SLOTS_PER_SUBJECT = 2
        
        # Daily limit for ENTIRE GROUP (max 5 blocks total per day) - can be relaxed if needed
        MAX_DAILY_SLOTS_FOR_GROUP = 5
        
        # Track if we need to relax group daily limit (fallback mode)
        relax_group_limit = False
        
        while slots_scheduled < slots_needed and week_offset < WEEKS_PER_SEMESTER * 2:
            best_candidate = None
            best_score = -float('inf')
            
            # Get current assigned entries for this subject to check limits
            current_assignment_entries = [e for e in schedule if e.teacher_subject_id == assignment.id]
            
            # Search for ONE best slot across all eligible weeks
            weeks_to_check = range(1 + week_offset, WEEKS_PER_SEMESTER + 1, week_interval)
            
            for week in weeks_to_check:
                if slots_scheduled >= slots_needed: break
                
                # Check weekly limit for this subject
                slots_this_week = sum(1 for e in current_assignment_entries if e.week_number == week)
                if slots_this_week >= max_slots_per_week:
                    continue
                
                # Check candidate slots (from preferences list)
                for slot_info in weekly_slot_scores:
                    day = slot_info['day']
                    slot = slot_info['slot']
                    
                    # Check daily limit for this subject (max 2 blocks of same subject)
                    slots_this_day_subject = sum(1 for e in current_assignment_entries if e.week_number == week and e.day_of_week == day)
                    if slots_this_day_subject >= MAX_DAILY_SLOTS_PER_SUBJECT:
                        continue
                    
                    # Check daily limit for entire group (max 5 blocks total)
                    # Only enforce if not in fallback mode
                    if not relax_group_limit:
                        group_slots_this_day = sum(1 for e in schedule if e.group_id == assignment.group_id and e.week_number == week and e.day_of_week == day)
                        if group_slots_this_day >= MAX_DAILY_SLOTS_FOR_GROUP:
                            continue
                    
                    base_pref = slot_info['score']
                    
                    if is_slot_occupied(assignment.teacher_id, assignment.group_id, week, day, slot):
                        continue
                    
                    occupied_rooms = get_occupied_rooms_at_slot(week, day, slot)
                    room = find_suitable_room(rooms, assignment.subject.type, group_size, occupied_rooms)
                    if not room:
                        continue
                    
                    # Calculate Dynamic Score based on Weights
                    w_pref = weights.get('preferences', 2)
                    w_t = weights.get('teacher_gaps', 2)
                    w_s = weights.get('student_gaps', 2)
                    
                    score = base_pref * w_pref * 2
                    
                    # Teacher Gaps Analysis
                    t_occupancy = teacher_occupancy.get(assignment.teacher_id, set())
                    t_has_classes_today = False
                    for k in t_occupancy:
                        if k.startswith(f"{week}-{day}-"):
                            t_has_classes_today = True
                            break
                    
                    if t_has_classes_today:
                        is_adj = f"{week}-{day}-{slot-1}" in t_occupancy or f"{week}-{day}-{slot+1}" in t_occupancy
                        if is_adj: 
                            score += 40 * w_t # Bonus for compactness
                        else: 
                            score -= 30 * w_t # Penalty for gap
                            
                    # Student Gaps Analysis
                    s_occupancy = group_occupancy.get(assignment.group_id, set())
                    s_has_classes_today = False
                    for k in s_occupancy:
                        if k.startswith(f"{week}-{day}-"):
                            s_has_classes_today = True
                            break
                            
                    if s_has_classes_today:
                        is_adj = f"{week}-{day}-{slot-1}" in s_occupancy or f"{week}-{day}-{slot+1}" in s_occupancy
                        if is_adj:
                            score += 40 * w_s
                        else:
                            score -= 30 * w_s
                    
                    if score > best_score:
                        best_score = score
                        best_candidate = {'week': week, 'day': day, 'slot': slot, 'room': room}
            
            if best_candidate:
                c = best_candidate
                entry = ScheduleEntry(
                    batch_id=batch.id,
                    semester=semester,
                    week_number=c['week'],
                    day_of_week=c['day'],
                    time_slot=c['slot'],
                    room_id=c['room'].id,
                    teacher_subject_id=assignment.id,
                    subject_id=assignment.subject_id,
                    group_id=assignment.group_id
                )
                schedule.append(entry)
                mark_slot_occupied(assignment.teacher_id, assignment.group_id, c['room'].id, 
                                 c['week'], c['day'], c['slot'])
                slots_scheduled += 1
            else:
                # No slot found with current constraints
                # FALLBACK: If we haven't relaxed the group limit yet, try relaxing it
                if not relax_group_limit:
                    relax_group_limit = True
                    # Don't increment week_offset, retry with relaxed limit
                    continue
                else:
                    # Already in fallback mode - increase offset and try again
                    week_offset += 1
        
        # Create conflict if not all scheduled
        if slots_scheduled < slots_needed:
            suggested_slots = []
            for week in range(1, WEEKS_PER_SEMESTER + 1):
                if len(suggested_slots) >= 8:
                    break
                for day in DAYS:
                    if len(suggested_slots) >= 8:
                        break
                    for slot in TIME_SLOTS:
                        if len(suggested_slots) >= 8:
                            break
                        if is_slot_occupied(assignment.teacher_id, assignment.group_id, week, day, slot):
                            continue
                        occupied_rooms = get_occupied_rooms_at_slot(week, day, slot)
                        room = find_suitable_room(rooms, assignment.subject.type, group_size, occupied_rooms)
                        if room:
                            suggested_slots.append({
                                'week': week,
                                'day': day,
                                'hour': slot,
                                'roomId': room.id,
                                'roomName': room.name
                            })
            
            conflicts.append({
                'id': f'conflict-{assignment.id}',
                'type': 'UNSCHEDULED',
                'description': f'Nie można zaplanować wszystkich bloków ({slots_scheduled}/{slots_needed})',
                'teacherSubjectId': assignment.id,
                'subjectName': assignment.subject.name,
                'teacherName': assignment.teacher.name,
                'groupName': assignment.group.name,
                'hoursScheduled': int(slots_scheduled * 1.5),
                'hoursNeeded': int(slots_needed * 1.5),
                'suggestedSlots': suggested_slots
            })
    
    # Save schedule to database
    if schedule:
        for entry in schedule:
            db.session.add(entry)
    
    # Calculate optimization metrics
    batch.preference_score = calculate_preference_score(schedule, preferences)
    batch.teacher_gaps = calculate_gaps(schedule, 'teacher')
    batch.student_gaps = calculate_gaps(schedule, 'student')
    
    db.session.commit()
    
    # Fetch entries from database to get proper relationships
    saved_entries = ScheduleEntry.query.filter_by(batch_id=batch.id).order_by(
        ScheduleEntry.week_number, ScheduleEntry.day_of_week, ScheduleEntry.time_slot
    ).all()
    
    return {
        'batch': batch.to_dict(),
        'schedule': [e.to_dict() for e in saved_entries],
        'conflicts': conflicts,
        'group': {'id': group.id, 'name': group.name},
        'semester': semester,
        'stats': {
            'totalEntries': len(saved_entries),
            'conflictsCount': len(conflicts),
            'weeksCount': WEEKS_PER_SEMESTER,
            'preferenceScore': batch.preference_score,
            'teacherGaps': batch.teacher_gaps,
            'studentGaps': batch.student_gaps
        }
    }


def reoptimize_drafts(batch_ids, semester=None, weights=None):
    """Re-optimize selected draft schedules together"""
    if semester is None:
        semester = get_current_semester()
    
    results = []
    
    # Get all batches to reoptimize
    batches = ScheduleBatch.query.filter(
        ScheduleBatch.id.in_(batch_ids),
        ScheduleBatch.status == 'DRAFT'
    ).all()
    
    if not batches:
        return {'error': 'No draft batches found'}
    
    # Reoptimize each batch in order
    for batch in batches:
        result = generate_schedule(
            group_id=batch.group_id,
            semester=batch.semester,
            existing_batch_id=batch.id,
            weights=weights
        )
        if 'error' not in result:
            results.append(result['batch'])
    
    return {
        'success': True,
        'reoptimized': results,
        'count': len(results)
    }


def publish_batches(batch_ids):
    """Publish selected draft schedules"""
    batches = ScheduleBatch.query.filter(
        ScheduleBatch.id.in_(batch_ids),
        ScheduleBatch.status == 'DRAFT'
    ).all()
    
    if not batches:
        return {'error': 'No draft batches found'}
    
    published = []
    for batch in batches:
        batch.status = 'PUBLISHED'
        batch.published_at = datetime.utcnow()
        published.append(batch.to_dict())
    
    db.session.commit()
    
    return {
        'success': True,
        'published': published,
        'count': len(published)
    }
