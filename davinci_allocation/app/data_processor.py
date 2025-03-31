import os
import json
import pandas as pd
from datetime import datetime, timedelta
from .models import Allocation, AllocationStatus

class DataProcessor:
    """
    deals with spreadsheet data & manages where we store all the allocation info
    """
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.allocations_file = os.path.join(data_dir, 'allocations.json')
        
        # make sure we have somewhere to save stuff
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # create empty json file if needed
        if not os.path.exists(self.allocations_file):
            with open(self.allocations_file, 'w') as f:
                json.dump([], f)
    
    def _load_allocations(self):
        """grab everything from our json file"""
        with open(self.allocations_file, 'r') as f:
            allocations_data = json.load(f)
        
        return [Allocation.from_dict(data) for data in allocations_data]
    
    def _save_allocations(self, allocations):
        """dump everything to json"""
        allocations_data = [allocation.to_dict() for allocation in allocations]
        
        with open(self.allocations_file, 'w') as f:
            json.dump(allocations_data, f, indent=2)
    
    def sync_from_spreadsheet(self, file_path=None):
        """
        pull in new data from the job form xlsx
        returns how many new ones we found
        """
        if file_path is None:
            file_path = os.getenv('JOB_FORM_SPREADSHEET', 'data/sample_job_forms.xlsx')
        
        # get what we already have
        allocations = self._load_allocations()
        existing_emails = {a.student_email for a in allocations}
        
        # open the spreadsheet
        df = pd.read_excel(file_path)
        
        # go through each new entry
        new_count = 0
        for index, row in df.iterrows():
            # skip if we've already got this one
            if row['student_email'] in existing_emails:
                continue
                
            # make a new allocation from row data
            allocation = Allocation(
                student_name=row['student_name'],
                student_email=row['student_email'],
                guardian_email=row['guardian_email'],
                request_email=row['request_email'],
                subjects=self._parse_subjects(row['subjects']),
                start_date=row['start_date'],
                package_hours=row['package_hours'],
                session_frequency=row['session_frequency'],
                student_availability=row['student_availability'],
                holiday_schedule=row['holiday_schedule'],
                additional_notes=row['additional_notes']
            )
            
            # add it to our list
            allocations.append(allocation)
            existing_emails.add(allocation.student_email)
            new_count += 1
        
        # save everything back
        self._save_allocations(allocations)
        
        return new_count
    
    def _parse_subjects(self, subjects_str):
        """split up subjects from comma/semicolon list"""
        if not subjects_str or pd.isna(subjects_str):
            return []
            
        if ';' in subjects_str:
            return [s.strip() for s in subjects_str.split(';') if s.strip()]
        else:
            return [s.strip() for s in subjects_str.split(',') if s.strip()]
    
    def get_pending_allocations(self):
        """get all the ones waiting to be worked on"""
        allocations = self._load_allocations()
        return [a for a in allocations if a.status == AllocationStatus.PENDING]
    
    def get_in_progress_allocations(self):
        """get all the ones someone is actively working on"""
        allocations = self._load_allocations()
        return [a for a in allocations if a.status == AllocationStatus.IN_PROGRESS]
    
    def get_completed_allocations(self):
        """get all the finished ones"""
        allocations = self._load_allocations()
        return [a for a in allocations if a.status == AllocationStatus.COMPLETED]
    
    def get_allocation_by_id(self, allocation_id):
        """find a specific allocation by ID"""
        allocations = self._load_allocations()
        for allocation in allocations:
            if allocation.id == allocation_id:
                return allocation
        return None
    
    def mark_as_in_progress(self, allocation_id, staff_member):
        """somebody's started working on this one"""
        allocations = self._load_allocations()
        
        for allocation in allocations:
            if allocation.id == allocation_id:
                allocation.status = AllocationStatus.IN_PROGRESS
                allocation.staff_member = staff_member
                allocation.date_started = datetime.now()
                break
        
        self._save_allocations(allocations)
    
    def mark_as_completed(self, allocation_id):
        """mark it as done!"""
        allocations = self._load_allocations()
        
        for allocation in allocations:
            if allocation.id == allocation_id:
                allocation.status = AllocationStatus.COMPLETED
                allocation.date_completed = datetime.now()
                break
        
        self._save_allocations(allocations)
    
    def split_subjects(self, allocation_id):
        """
        break a multi-subject req into separate ones for each subject
        returns the IDs of the new allocations we created
        """
        allocations = self._load_allocations()
        parent_allocation = None
        
        # gotta find the main one first
        for allocation in allocations:
            if allocation.id == allocation_id:
                parent_allocation = allocation
                break
        
        if not parent_allocation or len(parent_allocation.subjects) <= 1:
            # nothing to split or can't find it
            return []
        
        # make new allocations for each subject
        child_ids = []
        for subject in parent_allocation.subjects:
            # copy most info from the parent
            child = Allocation(
                student_name=parent_allocation.student_name,
                student_email=parent_allocation.student_email,
                guardian_email=parent_allocation.guardian_email,
                request_email=parent_allocation.request_email,
                subjects=[subject],  # just one subject now
                start_date=parent_allocation.start_date,
                package_hours=parent_allocation.package_hours,
                session_frequency=parent_allocation.session_frequency,
                student_availability=parent_allocation.student_availability,
                holiday_schedule=parent_allocation.holiday_schedule,
                additional_notes=self._filter_notes_for_subject(
                    parent_allocation.additional_notes, subject)
            )
            
            # setup the relationships
            child.parent_allocation_id = parent_allocation.id
            child.status = AllocationStatus.IN_PROGRESS
            child.staff_member = parent_allocation.staff_member
            child.date_started = parent_allocation.date_started
            child.current_subject = subject
            
            # add it to our records
            allocations.append(child)
            child_ids.append(child.id)
        
        # update the parent to link to kids
        parent_allocation.child_allocation_ids = child_ids
        parent_allocation.status = AllocationStatus.COMPLETED  # parent's job is done
        
        # save everything
        self._save_allocations(allocations)
        
        return child_ids
    
    def _filter_notes_for_subject(self, notes, subject):
        """just keep notes relevant to this specific subject"""
        if not notes:
            return ""
            
        # if it mentions the subject, keep it
        subject_keywords = subject.lower().split()
        lines = notes.split('\n')
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            # keep lines with subject keywords or general notes (no subject)
            if any(keyword in line_lower for keyword in subject_keywords) or not any(
                    subject_name.lower() in line_lower for subject_name in ['english', 'math', 'science']):
                relevant_lines.append(line)
        
        return '\n'.join(relevant_lines)
    
    def update_matching_teachers(self, allocation_id, matching_teachers):
        """save a list of teachers that might work for this allocation"""
        allocations = self._load_allocations()
        
        for allocation in allocations:
            if allocation.id == allocation_id:
                allocation.matching_teachers = matching_teachers
                break
        
        self._save_allocations(allocations)
    
    def add_invited_teacher(self, allocation_id, teacher_id):
        """track that we invited a teacher"""
        allocations = self._load_allocations()
        
        for allocation in allocations:
            if allocation.id == allocation_id:
                if teacher_id not in allocation.invited_teachers:
                    allocation.invited_teachers.append(teacher_id)
                break
        
        self._save_allocations(allocations)
    
    def confirm_teacher(self, allocation_id, teacher_info):
        """a teacher said yes! save their info"""
        allocations = self._load_allocations()
        
        for allocation in allocations:
            if allocation.id == allocation_id:
                allocation.confirmed_teacher = teacher_info
                break
        
        self._save_allocations(allocations)
    
    def get_statistics(self):
        """grab some stats about our allocations for the dashboard"""
        allocations = self._load_allocations()
        
        # basic counts
        total = len(allocations)
        pending = sum(1 for a in allocations if a.status == AllocationStatus.PENDING)
        in_progress = sum(1 for a in allocations if a.status == AllocationStatus.IN_PROGRESS)
        completed = sum(1 for a in allocations if a.status == AllocationStatus.COMPLETED)
        
        # how long it takes to complete allocations
        completion_times = []
        for allocation in allocations:
            if (allocation.status == AllocationStatus.COMPLETED and 
                allocation.date_completed and allocation.date_created):
                time_diff = allocation.date_completed - allocation.date_created
                completion_times.append(time_diff.total_seconds() / 3600)  # in hrs
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # what subjects are popular
        subjects_count = {}
        for allocation in allocations:
            for subject in allocation.subjects:
                subjects_count[subject] = subjects_count.get(subject, 0) + 1
        
        return {
            'total_allocations': total,
            'pending_allocations': pending,
            'in_progress_allocations': in_progress,
            'completed_allocations': completed,
            'avg_completion_time_hours': avg_completion_time,
            'subjects_count': subjects_count
        } 