import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Job, Candidate
from datetime import datetime, timedelta
import secrets
import os
from flask import current_app

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Set the logging level

@admin.route('/')
def index():
    jobs = Job.query.all()
    active_jobs = sum(1 for job in jobs if job.is_active and not job.is_expired())
    total_candidates = Candidate.query.count()
    return render_template('admin/dashboard.html', 
                         jobs=jobs, 
                         active_jobs=active_jobs,
                         total_candidates=total_candidates)

@admin.route('/jobs/new', methods=['GET', 'POST'])
def new_job():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        days_valid = int(request.form.get('days_valid', 0))
        hours_valid = int(request.form.get('hours_valid', 0))
        minutes_valid = int(request.form.get('minutes_valid', 0))
        
        # Ensure at least one time unit is provided
        if days_valid == 0 and hours_valid == 0 and minutes_valid == 0:
            flash('Please specify a valid time duration', 'error')
            return redirect(url_for('admin.new_job'))
        
        job = Job(title=title, description=description)
        db.session.add(job)
        db.session.commit()
        
        # Generate link with custom expiry time
        job.generate_link(days_valid=days_valid, hours_valid=hours_valid, minutes_valid=minutes_valid)
        
        flash('Job created successfully!', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/new_job.html')

@admin.route('/view_job/<int:job_id>')
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    candidates = Candidate.query.filter_by(job_id=job_id).all()
    return render_template('admin/view_job.html', job=job, candidates=candidates)

@admin.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.description = request.form.get('description')
        job.is_active = 'is_active' in request.form
        
        # Convert string dates to datetime objects
        job.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        job.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('admin.view_job', job_id=job.id))
    
    return render_template('admin/edit_job.html', job=job)

@admin.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Delete associated candidates
    Candidate.query.filter_by(job_id=job_id).delete()
    
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('admin.index'))

@admin.route('/toggle_job/<int:job_id>')
def toggle_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        job.is_active = not job.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_active': job.is_active,
            'message': f'Job {"activated" if job.is_active else "deactivated"} successfully!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin.route('/candidates')
def view_candidates():
    """View all candidates or filter by job"""
    job_id = request.args.get('job_id', type=int)
    
    # Get all jobs for the filter dropdown
    jobs = Job.query.order_by(Job.title).all()
    
    # Filter candidates if job_id is provided
    if job_id:
        candidates = Candidate.query.filter_by(job_id=job_id).order_by(Candidate.submitted_at.desc()).all()
    else:
        candidates = Candidate.query.order_by(Candidate.submitted_at.desc()).all()
    
    return render_template('admin/candidates.html', 
                         candidates=candidates,
                         jobs=jobs,
                         selected_job_id=job_id)

@admin.route('/api/candidates')
def get_candidates():
    """API endpoint for candidates data"""
    candidates = Candidate.query.all()
    return jsonify([{
        'id': c.id,
        'job_id': c.job_id,
        'name': f"{c.first_name} {c.last_name}",
        'email': c.personal_email,
        'mobile': c.mobile_no,
        'experience': c.total_experience,
        'skills': c.primary_skills,
        'submitted_at': c.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    } for c in candidates])

@admin.route('/delete_candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    try:
        # Delete associated files
        if candidate.resume_attachments:
            resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', candidate.resume_attachments)
            if os.path.exists(resume_path):
                os.remove(resume_path)
        
        if candidate.self_introduction_video:
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos', candidate.self_introduction_video)
            if os.path.exists(video_path):
                os.remove(video_path)
        
        # Delete the candidate record
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
