import uuid
from datetime import datetime
from enum import Enum

class AllocationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Allocation:
    """
    this is for handling a student + specific subject combo in the da vinci program
    """
    def __init__(self, 
                 student_name, 
                 student_email, 
                 guardian_email, 
                 request_email, 
                 subjects, 
                 start_date, 
                 package_hours, 
                 session_frequency,
                 student_availability, 
                 holiday_schedule, 
                 additional_notes):
        self.id = str(uuid.uuid4())
        self.student_name = student_name
        self.student_email = student_email
        self.guardian_email = guardian_email
        self.request_email = request_email
        self.subjects = subjects  # all the subjs they want
        self.current_subject = None  # we'll set this after splitting
        self.all_subjects = subjects  # keeping og list just in case
        self.start_date = start_date
        self.end_date = None  # will figure this out later
        self.package_hours = package_hours
        self.session_frequency = session_frequency
        self.student_availability = student_availability
        self.holiday_schedule = holiday_schedule
        self.additional_notes = additional_notes
        
        # tracking where we are in the process
        self.status = AllocationStatus.PENDING
        self.staff_member = None
        self.date_created = datetime.now()
        self.date_started = None
        self.date_completed = None
        
        # teacher stuff
        self.matching_teachers = []  # teachers we might assign
        self.invited_teachers = []  # ones we asked
        self.confirmed_teacher = None  # the one who said yes
        
        # for multi-subject allocations
        self.parent_allocation_id = None
        self.child_allocation_ids = []
    
    def to_dict(self):
        """turns this obj into a dict for json etc"""
        return {
            'id': self.id,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'guardian_email': self.guardian_email,
            'request_email': self.request_email,
            'subjects': self.subjects,
            'current_subject': self.current_subject,
            'all_subjects': self.all_subjects,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'package_hours': self.package_hours,
            'session_frequency': self.session_frequency,
            'student_availability': self.student_availability,
            'holiday_schedule': self.holiday_schedule,
            'additional_notes': self.additional_notes,
            'status': self.status.value,
            'staff_member': self.staff_member,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_started': self.date_started.isoformat() if self.date_started else None,
            'date_completed': self.date_completed.isoformat() if self.date_completed else None,
            'matching_teachers': self.matching_teachers,
            'invited_teachers': self.invited_teachers,
            'confirmed_teacher': self.confirmed_teacher,
            'parent_allocation_id': self.parent_allocation_id,
            'child_allocation_ids': self.child_allocation_ids
        }
    
    @classmethod
    def from_dict(cls, data):
        """goes from a dict back to an allocation - needed when loading from json"""
        allocation = cls(
            student_name=data.get('student_name'),
            student_email=data.get('student_email'),
            guardian_email=data.get('guardian_email'),
            request_email=data.get('request_email'),
            subjects=data.get('subjects', []),
            start_date=data.get('start_date'),
            package_hours=data.get('package_hours'),
            session_frequency=data.get('session_frequency'),
            student_availability=data.get('student_availability'),
            holiday_schedule=data.get('holiday_schedule'),
            additional_notes=data.get('additional_notes')
        )
        
        # put the ID back if we have it
        if 'id' in data:
            allocation.id = data['id']
            
        # get all the other props back
        allocation.current_subject = data.get('current_subject')
        allocation.all_subjects = data.get('all_subjects', data.get('subjects', []))
        allocation.end_date = data.get('end_date')
        allocation.status = AllocationStatus(data.get('status', 'pending'))
        allocation.staff_member = data.get('staff_member')
        
        # bring back the dates
        if data.get('date_created'):
            allocation.date_created = datetime.fromisoformat(data['date_created'])
        if data.get('date_started'):
            allocation.date_started = datetime.fromisoformat(data['date_started'])
        if data.get('date_completed'):
            allocation.date_completed = datetime.fromisoformat(data['date_completed'])
            
        # teacher matching stuff
        allocation.matching_teachers = data.get('matching_teachers', [])
        allocation.invited_teachers = data.get('invited_teachers', [])
        allocation.confirmed_teacher = data.get('confirmed_teacher')
        
        # parent/child stuff from multi-subject
        allocation.parent_allocation_id = data.get('parent_allocation_id')
        allocation.child_allocation_ids = data.get('child_allocation_ids', [])
        
        return allocation 