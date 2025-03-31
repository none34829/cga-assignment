from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from app.models import Allocation
from app.data_processor import DataProcessor
from app.teacher_matcher import TeacherMatcher
from app.email_service import EmailService
from app.crimson_api import CrimsonAPI

# grab our env vars
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_key_for_testing')

# setup all our services
data_processor = DataProcessor()
teacher_matcher = TeacherMatcher()
email_service = EmailService()
crimson_api = CrimsonAPI(
    api_key=os.getenv('CRIMSON_APP_API_KEY', 'test_key')
)

@app.route('/')
def dashboard():
    """main page showing what allocations we've got"""
    pending_allocations = data_processor.get_pending_allocations()
    in_progress_allocations = data_processor.get_in_progress_allocations()
    completed_allocations = data_processor.get_completed_allocations()
    
    return render_template(
        'dashboard.html',
        pending=pending_allocations,
        in_progress=in_progress_allocations,
        completed=completed_allocations
    )

@app.route('/allocation/<allocation_id>', methods=['GET'])
def view_allocation(allocation_id):
    """look at the details for one specific allocation"""
    allocation = data_processor.get_allocation_by_id(allocation_id)
    if not allocation:
        flash('Allocation not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('allocation_details.html', allocation=allocation)

@app.route('/allocation/<allocation_id>/start', methods=['POST'])
def start_allocation(allocation_id):
    """mark this one as started and get it ready"""
    allocation = data_processor.get_allocation_by_id(allocation_id)
    if not allocation:
        flash('Allocation not found', 'error')
        return redirect(url_for('dashboard'))
    
    # mark it as in progress
    data_processor.mark_as_in_progress(allocation_id, request.form.get('staff_member'))
    
    # split it up if it's got multiple subjects
    data_processor.split_subjects(allocation_id)
    
    flash('Allocation marked as in-progress', 'success')
    return redirect(url_for('dashboard'))

@app.route('/allocation/<allocation_id>/match', methods=['POST'])
def match_teachers(allocation_id):
    """find some teachers that might work for this one"""
    allocation = data_processor.get_allocation_by_id(allocation_id)
    if not allocation:
        flash('Allocation not found', 'error')
        return redirect(url_for('dashboard'))
    
    # run our matching algo
    matching_teachers = teacher_matcher.find_matching_teachers(allocation)
    
    # save the results
    data_processor.update_matching_teachers(allocation_id, matching_teachers)
    
    flash('Teacher matching completed', 'success')
    return redirect(url_for('view_allocation', allocation_id=allocation_id))

@app.route('/allocation/<allocation_id>/invite', methods=['POST'])
def send_invitations(allocation_id):
    """ask some teachers if they want this student"""
    allocation = data_processor.get_allocation_by_id(allocation_id)
    if not allocation:
        flash('Allocation not found', 'error')
        return redirect(url_for('dashboard'))
    
    selected_teacher_ids = request.form.getlist('selected_teachers')
    if not selected_teacher_ids:
        flash('No teachers selected', 'error')
        return redirect(url_for('view_allocation', allocation_id=allocation_id))
    
    # send out the invites via crimson
    for teacher_id in selected_teacher_ids:
        success = crimson_api.send_teacher_invitation(allocation, teacher_id)
        if success:
            data_processor.add_invited_teacher(allocation_id, teacher_id)
    
    flash('Invitations sent to teachers', 'success')
    return redirect(url_for('view_allocation', allocation_id=allocation_id))

@app.route('/allocation/<allocation_id>/confirm', methods=['POST'])
def confirm_teacher(allocation_id):
    """a teacher said yes! let everyone know"""
    allocation = data_processor.get_allocation_by_id(allocation_id)
    if not allocation:
        flash('Allocation not found', 'error')
        return redirect(url_for('dashboard'))
    
    teacher_id = request.form.get('accepted_teacher_id')
    if not teacher_id:
        flash('No teacher specified', 'error')
        return redirect(url_for('view_allocation', allocation_id=allocation_id))
    
    # save the teacher's info
    teacher_info = crimson_api.get_teacher_info(teacher_id)
    data_processor.confirm_teacher(allocation_id, teacher_info)
    
    # send out the emails
    email_service.send_confirmation_email(allocation, teacher_info)
    
    # mark it as done
    data_processor.mark_as_completed(allocation_id)
    
    flash('Teacher confirmed and emails sent', 'success')
    return redirect(url_for('dashboard'))

@app.route('/sync', methods=['POST'])
def sync_data():
    """pull in new data from the spreadsheet"""
    new_count = data_processor.sync_from_spreadsheet()
    flash(f'{new_count} new allocations imported', 'success')
    return redirect(url_for('dashboard'))

@app.route('/stats')
def statistics():
    """check out some numbers about how we're doing"""
    stats = data_processor.get_statistics()
    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True) 