import requests
import json
import os
from datetime import datetime, timedelta
import random

class CrimsonAPI:
    """
    connects to the crimson app for getting student/teacher data
    and doing teacher assignments
    """
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv('CRIMSON_APP_API_KEY', 'test_key')
        self.base_url = base_url or os.getenv('CRIMSON_APP_API_URL', 'https://api.crimsonapp.example.com')
        
        # if testing, use the fake mock API instead of real one
        self.use_mock = (self.api_key == 'test_key')
        
        # need a place to store our fake data
        if self.use_mock and not os.path.exists('data'):
            os.makedirs('data')
            
            # create some teachers etc
            self._initialize_mock_data()
    
    def get_student_info(self, student_id):
        """grab basic info about a student"""
        if self.use_mock:
            return self._mock_get_student_info(student_id)
            
        url = f"{self.base_url}/students/{student_id}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def add_subject(self, student_id, subject_info):
        """add a new subject to a student's list"""
        if self.use_mock:
            return self._mock_add_subject(student_id, subject_info)
            
        url = f"{self.base_url}/students/{student_id}/subjects"
        headers = self._get_headers()
        
        response = requests.post(url, headers=headers, json=subject_info)
        return self._handle_response(response)
    
    def get_available_teachers(self, subject):
        """find teachers who can teach this subject"""
        if self.use_mock:
            return self._mock_get_available_teachers(subject)
            
        url = f"{self.base_url}/teachers/available"
        headers = self._get_headers()
        params = {'subject': subject}
        
        response = requests.get(url, headers=headers, params=params)
        return self._handle_response(response)
    
    def send_teacher_invitation(self, allocation, teacher_id):
        """invite a teacher to take on this student"""
        if self.use_mock:
            return self._mock_send_teacher_invitation(allocation, teacher_id)
            
        url = f"{self.base_url}/invitations"
        headers = self._get_headers()
        
        invitation_data = {
            'teacher_id': teacher_id,
            'student_id': allocation.student_id,
            'subject': allocation.current_subject or allocation.subjects[0],
            'start_date': allocation.start_date,
            'end_date': allocation.end_date,
            'total_hours': allocation.package_hours,
            'session_frequency': allocation.session_frequency,
            'additional_notes': f"Student Availability: {allocation.student_availability}\n"
                               f"Holiday Schedule: {allocation.holiday_schedule}\n"
                               f"Notes: {allocation.additional_notes}"
        }
        
        response = requests.post(url, headers=headers, json=invitation_data)
        return self._handle_response(response)
    
    def get_teacher_info(self, teacher_id):
        """get details about a specific teacher"""
        if self.use_mock:
            return self._mock_get_teacher_info(teacher_id)
            
        url = f"{self.base_url}/teachers/{teacher_id}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def get_teacher_workload(self, teacher_id):
        """check how many students a teacher has, hours, etc"""
        if self.use_mock:
            return self._mock_get_teacher_workload(teacher_id)
            
        url = f"{self.base_url}/teachers/{teacher_id}/workload"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def _get_headers(self):
        """setup auth headers for API calls"""
        return {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _handle_response(self, response):
        """check if we got a good response, handle errors"""
        if response.status_code in (200, 201, 204):
            if response.content:
                return response.json()
            return True
        else:
            # something went wrong :(
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    
    # all the mock stuff below is just for testing
    def _initialize_mock_data(self):
        """make up some fake teachers for testing"""
        teachers_data = []
        
        # names for our fake teachers
        teacher_names = [
            "John Smith", "Maria Garcia", "Li Wei", "Alex Johnson", 
            "Sophia Williams", "Raj Patel", "Emma Brown", "Carlos Rodriguez",
            "Aisha Khan", "Olivia Davis", "David Wilson", "Carrie Cambear"
        ]
        
        # subjects by area
        subjects = {
            "English": ["English 7", "English 8", "English 9"],
            "Math": ["Math 7", "Math 8", "Algebra", "Geometry"],
            "Science": ["Earth and Space Science 7", "Biology", "Chemistry", "Physics"]
        }
        
        for i, name in enumerate(teacher_names):
            # pick some random subjects for this teacher
            teacher_subject_areas = random.sample(list(subjects.keys()), k=random.randint(1, 2))
            teacher_subjects = []
            for area in teacher_subject_areas:
                teacher_subjects.extend(random.sample(subjects[area], k=random.randint(1, len(subjects[area]))))
            
            # make the teacher object
            teacher = {
                'id': f"t{i+1:03d}",
                'name': name,
                'email': f"{name.lower().replace(' ', '.')}@cga.edu",
                'subjects': teacher_subjects,
                'active_students': random.randint(5, 40),
                'subject_expertise': random.randint(3, 5),
                'average_rating': round(random.uniform(3.5, 5.0), 1),
                'availability': {
                    'weekdays': ['Monday', 'Wednesday', 'Friday'] if i % 2 == 0 else ['Tuesday', 'Thursday'],
                    'time_slots': ["8:00-10:00", "13:00-15:00", "16:00-18:00"]
                }
            }
            
            # special case from the transcript video
            if "Carrie" in name:
                teacher['id'] = "t999"  # easier to find
                teacher['active_students'] = 14  # like in the video
            
            teachers_data.append(teacher)
        
        # save our fake teachers
        with open('data/mock_teachers.json', 'w') as f:
            json.dump(teachers_data, f, indent=2)
    
    def _get_mock_data(self, file_name):
        """load data from our json files"""
        try:
            with open(f'data/{file_name}', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_mock_data(self, file_name, data):
        """save data to our json files"""
        with open(f'data/{file_name}', 'w') as f:
            json.dump(data, f, indent=2)
    
    def _mock_get_student_info(self, student_id):
        """fake version of get_student_info"""
        # just make up a student
        return {
            'id': student_id,
            'name': 'Test Student',
            'email': 'student@example.com',
            'subjects': []
        }
    
    def _mock_add_subject(self, student_id, subject_info):
        """fake version of add_subject"""
        # pretend it worked
        return True
    
    def _mock_get_available_teachers(self, subject):
        """fake version of get_available_teachers"""
        teachers = self._get_mock_data('mock_teachers.json')
        
        # find teachers who know this subject
        available_teachers = []
        for teacher in teachers:
            if subject in teacher['subjects']:
                available_teachers.append(teacher)
        
        return available_teachers
    
    def _mock_send_teacher_invitation(self, allocation, teacher_id):
        """fake version of send_teacher_invitation"""
        # always works in test mode
        return True
    
    def _mock_get_teacher_info(self, teacher_id):
        """fake version of get_teacher_info"""
        teachers = self._get_mock_data('mock_teachers.json')
        
        for teacher in teachers:
            if teacher['id'] == teacher_id:
                return teacher
        
        return None
    
    def _mock_get_teacher_workload(self, teacher_id):
        """fake version of get_teacher_workload"""
        teachers = self._get_mock_data('mock_teachers.json')
        
        for teacher in teachers:
            if teacher['id'] == teacher_id:
                # make up some workload numbers
                return {
                    'active_students': teacher['active_students'],
                    'hours_per_week': round(teacher['active_students'] * 1.5, 1),
                    'available_capacity': max(0, 50 - teacher['active_students'] * 1.5)
                }
        
        return None 