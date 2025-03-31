import os
import pandas as pd
from datetime import datetime, timedelta

def create_sample_job_forms():
    """Create a sample job forms Excel file for testing"""
    
    # create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # sample data
    data = {
        'student_name': [
            'Britney Blue Cheese',
            'Alex Appleton',
            'Charlie Chen',
            'Dakota Devon',
            'Eliot Edwards'
        ],
        'student_email': [
            'britney.bluecheese@example.com',
            'alex.appleton@example.com',
            'charlie.chen@example.com',
            'dakota.devon@example.com',
            'eliot.edwards@example.com'
        ],
        'guardian_email': [
            'parent.bluecheese@example.com',
            'parent.appleton@example.com',
            'parent.chen@example.com',
            'parent.devon@example.com',
            'parent.edwards@example.com'
        ],
        'request_email': [
            'ao.bluecheese@cga.edu',
            'ao.appleton@cga.edu',
            'ao.chen@cga.edu',
            'ao.devon@cga.edu',
            'ao.edwards@cga.edu'
        ],
        'subjects': [
            'US Junior High English 7, US Junior High Math 8, US Junior High Earth and Space Science 7',
            'US Junior High Math 7, US Junior High English 7',
            'US Junior High Science 8',
            'US Junior High Math 8, US Junior High English 8',
            'US Junior High English 7, US Junior High Science 7'
        ],
        'start_date': [
            (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        ],
        'package_hours': [
            20,
            16,
            10,
            24,
            15
        ],
        'session_frequency': [
            '2 times 1 hour sessions per week',
            '2 times 1 hour sessions per week',
            '1 time 1 hour session per week',
            '3 times 1 hour sessions per week',
            '1 time 1.5 hour session per week'
        ],
        'student_availability': [
            'Monday-Friday, 3:00 PM - 7:00 PM EST',
            'Tuesday, Thursday, Saturday 4:00 PM - 8:00 PM EST',
            'Monday, Wednesday, Friday 5:00 PM - 9:00 PM EST',
            'Weekdays 2:00 PM - 6:00 PM EST',
            'Monday, Thursday 3:30 PM - 7:30 PM EST'
        ],
        'holiday_schedule': [
            'Unavailable Dec 20 - Jan 5, Spring Break March 15-22',
            'Unavailable Nov 23-27, Dec 22 - Jan 3',
            'Unavailable Dec 15 - Jan 10',
            'Unavailable Dec 18 - Jan 2',
            'Unavailable Dec 21 - Jan 4, April 10-17'
        ],
        'additional_notes': [
            'Student prefers female teachers for English. Coordinating with other activities so schedule must be consistent.',
            'Student has ADHD, prefers shorter sessions with breaks.',
            'Student has advanced knowledge in biology but needs help with physics concepts.',
            'Student is advanced in math but struggles with English comprehension.',
            'Student prefers visual learning approaches. Needs extra support with writing.'
        ]
    }
    
    # create a dataframe
    df = pd.DataFrame(data)
    
    # save to excel
    output_path = 'data/sample_job_forms.xlsx'
    df.to_excel(output_path, index=False)
    
    print(f"Sample data created at {output_path}")

if __name__ == "__main__":
    create_sample_job_forms() 