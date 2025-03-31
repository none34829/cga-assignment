import os
import sys
import unittest
from app.models import Allocation, AllocationStatus
from app.data_processor import DataProcessor
from app.teacher_matcher import TeacherMatcher
from app.email_service import EmailService
from app.crimson_api import CrimsonAPI
from dotenv import load_dotenv

# grab our env vars
load_dotenv()

class TestDaVinciAllocationSystem(unittest.TestCase):
    """test cases for our da vinci allocation system"""
    
    def setUp(self):
        """get everything ready for testing"""
        # use a separate folder for test data
        self.test_data_dir = 'test_data'
        if not os.path.exists(self.test_data_dir):
            os.makedirs(self.test_data_dir)
        
        # setup all our test components
        self.data_processor = DataProcessor(data_dir=self.test_data_dir)
        self.teacher_matcher = TeacherMatcher()
        self.email_service = EmailService()
        self.crimson_api = CrimsonAPI()
    
    def tearDown(self):
        """clean up our test files"""
        # remove the test data file
        allocations_file = os.path.join(self.test_data_dir, 'allocations.json')
        if os.path.exists(allocations_file):
            os.remove(allocations_file)
    
    def test_allocation_creation(self):
        """make sure we can create an allocation properly"""
        allocation = Allocation(
            student_name="Test Student",
            student_email="test@example.com",
            guardian_email="parent@example.com",
            request_email="ao@cga.edu",
            subjects=["Math", "English"],
            start_date="2023-01-01",
            package_hours=20,
            session_frequency="2 times per week",
            student_availability="Weekdays 4-8pm",
            holiday_schedule="Dec 24-Jan 2",
            additional_notes="Test notes"
        )
        
        # check the basic stuff
        self.assertEqual(allocation.student_name, "Test Student")
        self.assertEqual(allocation.status, AllocationStatus.PENDING)
        self.assertEqual(len(allocation.subjects), 2)
    
    def test_allocation_serialization(self):
        """make sure we can save and load allocations"""
        # create a test allocation
        original = Allocation(
            student_name="Test Student",
            student_email="test@example.com",
            guardian_email="parent@example.com",
            request_email="ao@cga.edu",
            subjects=["Math", "English"],
            start_date="2023-01-01",
            package_hours=20,
            session_frequency="2 times per week",
            student_availability="Weekdays 4-8pm",
            holiday_schedule="Dec 24-Jan 2",
            additional_notes="Test notes"
        )
        
        # save it to a dict
        data = original.to_dict()
        
        # load it back from the dict
        reconstructed = Allocation.from_dict(data)
        
        # make sure everything came back ok
        self.assertEqual(reconstructed.id, original.id)
        self.assertEqual(reconstructed.student_name, original.student_name)
        self.assertEqual(reconstructed.subjects, original.subjects)
        self.assertEqual(reconstructed.status.value, original.status.value)
    
    def test_data_processor_operations(self):
        """test the basic data processor stuff"""
        # make a test allocation
        allocation = Allocation(
            student_name="Test Student",
            student_email="test@example.com",
            guardian_email="parent@example.com",
            request_email="ao@cga.edu",
            subjects=["Math", "English"],
            start_date="2023-01-01",
            package_hours=20,
            session_frequency="2 times per week",
            student_availability="Weekdays 4-8pm",
            holiday_schedule="Dec 24-Jan 2",
            additional_notes="Test notes"
        )
        
        # save it
        allocations = [allocation]
        self.data_processor._save_allocations(allocations)
        
        # load it back
        loaded = self.data_processor._load_allocations()
        
        # check it loaded right
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].id, allocation.id)
        
        # test changing status
        self.data_processor.mark_as_in_progress(allocation.id, "Test Staff")
        loaded = self.data_processor._load_allocations()
        self.assertEqual(loaded[0].status, AllocationStatus.IN_PROGRESS)
        self.assertEqual(loaded[0].staff_member, "Test Staff")
        
        self.data_processor.mark_as_completed(allocation.id)
        loaded = self.data_processor._load_allocations()
        self.assertEqual(loaded[0].status, AllocationStatus.COMPLETED)
    
    def test_subject_splitting(self):
        """test breaking up multi-subject allocations"""
        # make a test with multiple subjects
        allocation = Allocation(
            student_name="Test Student",
            student_email="test@example.com",
            guardian_email="parent@example.com",
            request_email="ao@cga.edu",
            subjects=["Math", "English", "Science"],
            start_date="2023-01-01",
            package_hours=20,
            session_frequency="2 times per week",
            student_availability="Weekdays 4-8pm",
            holiday_schedule="Dec 24-Jan 2",
            additional_notes="Math: needs algebra help. English: focus on writing."
        )
        
        # save it
        allocations = [allocation]
        self.data_processor._save_allocations(allocations)
        
        # mark as started first
        self.data_processor.mark_as_in_progress(allocation.id, "Test Staff")
        
        # split it up
        child_ids = self.data_processor.split_subjects(allocation.id)
        
        # should have 3 new ones
        self.assertEqual(len(child_ids), 3)
        
        # load everything back
        loaded = self.data_processor._load_allocations()
        
        # should have 4 total now (1 parent + 3 kids)
        self.assertEqual(len(loaded), 4)
        
        # parent should be done
        parent = next(a for a in loaded if a.id == allocation.id)
        self.assertEqual(parent.status, AllocationStatus.COMPLETED)
        self.assertEqual(len(parent.child_allocation_ids), 3)
        
        # each kid should have one subject
        children = [a for a in loaded if a.id in child_ids]
        self.assertEqual(len(children), 3)
        
        for child in children:
            self.assertEqual(len(child.subjects), 1)
            self.assertEqual(child.parent_allocation_id, allocation.id)
            self.assertEqual(child.status, AllocationStatus.IN_PROGRESS)
    
    def test_mock_api(self):
        """test our fake crimson API"""
        # setup some fake data
        self.crimson_api._initialize_mock_data()
        
        # try getting some teachers
        teachers = self.crimson_api.get_available_teachers("English 7")
        
        # should get something back
        self.assertIsNotNone(teachers)

if __name__ == '__main__':
    unittest.main()