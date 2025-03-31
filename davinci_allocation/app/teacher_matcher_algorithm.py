from .crimson_api import CrimsonAPI
import os

class TeacherMatcher:
    """
    finds the best teachers for each student based on a bunch of factors
    """
    def __init__(self):
        self.crimson_api = CrimsonAPI(
            api_key=os.getenv('CRIMSON_APP_API_KEY', 'test_key')
        )
    
    def find_matching_teachers(self, allocation):
        """
        looks for teachers that match this allocation
        gives back a list with all their info + scores
        """
        # figure out which subject we need
        subject = allocation.current_subject
        if not subject and allocation.subjects:
            subject = allocation.subjects[0]
        
        if not subject:
            return []
            
        # ask the API for available teachers
        available_teachers = self.crimson_api.get_available_teachers(subject)
        
        # rate each teacher with our algorithm
        scored_teachers = self._score_teachers(available_teachers, allocation)
        
        # best matches first
        scored_teachers.sort(key=lambda t: t['score'], reverse=True)
        
        return scored_teachers
    
    def _score_teachers(self, teachers, allocation):
        """
        ranks teachers based on:
        - how many students they already have
        - how good they are at this subject
        - if their schedule works with the student
        - ratings from past students
        """
        scored_teachers = []
        
        for teacher in teachers:
            score = 100  # start at 100pts
            
            # too many students = bad
            student_count = teacher.get('active_students', 0)
            if student_count > 30:
                score -= 20  # way too many students
            elif student_count > 20:
                score -= 10  # kinda busy
            elif student_count < 10:
                score += 10  # nice and available
            
            # how good are they at this subject? (1-5 scale)
            subject_expertise = teacher.get('subject_expertise', 3)
            score += (subject_expertise - 3) * 5  # -10 to +10 pts
            
            # can they actually meet when the student is free?
            compatibility = self._calculate_schedule_compatibility(
                teacher.get('availability', {}),
                allocation.student_availability
            )
            score += compatibility * 20  # 0 to 20 pts
            
            # past ratings (1-5 scale)
            rating = teacher.get('average_rating', 4.0)
            score += (rating - 4.0) * 10  # -30 to +10 pts
            
            # add the score to the teacher's info
            teacher_with_score = dict(teacher)
            teacher_with_score['score'] = round(score, 2)
            scored_teachers.append(teacher_with_score)
        
        return scored_teachers
    
    def _calculate_schedule_compatibility(self, teacher_availability, student_availability):
        """
        checks how well schedules line up
        returns 0 (no overlap) to 1 (perfect match)
        """
        # super simplified for now
        # in real life we'd parse the text and compare time slots
        
        # just random for demo purposes
        # TODO: actually implement proper schedule parsing & matching
        import random
        return random.uniform(0.5, 1.0)
    
    def get_teacher_workload(self, teacher_id):
        """check how busy this teacher is"""
        return self.crimson_api.get_teacher_workload(teacher_id) 