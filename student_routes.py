import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db, StudentProfile, PlacementDrive, Application
from functools import wraps
from datetime import date
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def student_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if student and student.is_blacklisted:
            flash('Your account has been blacklisted. Contact admin.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()

    approved_drives = (
        PlacementDrive.query
        .filter_by(status='approved')
        .filter(PlacementDrive.application_deadline >= date.today())
        .order_by(PlacementDrive.application_deadline.asc())
        .limit(5)
        .all()
    )

    my_applications = (
        Application.query
        .filter_by(student_id=student.id)
        .order_by(Application.applied_date.desc())
        .all()
    )

    applied_count = len(my_applications)
    shortlisted_count = sum(1 for a in my_applications if a.status == 'Shortlisted')
    selected_count = sum(1 for a in my_applications if a.status == 'Selected')

    applied_drive_ids = {a.drive_id for a in my_applications}

    return render_template('student/dashboard.html',
                           student=student,
                           approved_drives=approved_drives,
                           my_applications=my_applications,
                           applied_count=applied_count,
                           shortlisted_count=shortlisted_count,
                           selected_count=selected_count,
                           applied_drive_ids=applied_drive_ids)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        student.name = request.form.get('name', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.department = request.form.get('department', '').strip()
        student.cgpa = float(request.form.get('cgpa', '0') or '0')
        student.skills = request.form.get('skills', '').strip()
        student.about = request.form.get('about', '').strip()
        grad_year = request.form.get('graduation_year', '')
        student.graduation_year = int(grad_year) if grad_year else None

        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{student.roll_number}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                student.resume_path = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', student=student)


@student_bp.route('/drives')
@student_required
def browse_drives():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    search = request.args.get('q', '').strip()

    query = (
        PlacementDrive.query
        .filter_by(status='approved')
        .filter(PlacementDrive.application_deadline >= date.today())
    )

    if search:
        query = query.filter(
            db.or_(
                PlacementDrive.job_title.ilike(f'%{search}%'),
                PlacementDrive.location.ilike(f'%{search}%'),
                PlacementDrive.job_type.ilike(f'%{search}%')
            )
        )

    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()

    applied_drive_ids = {
        a.drive_id for a in Application.query.filter_by(student_id=student.id).all()
    }

    return render_template('student/browse_drives.html',
                           drives=drives,
                           applied_drive_ids=applied_drive_ids,
                           search=search,
                           student=student)


@student_bp.route('/drive/<int:drive_id>')
@student_required
def drive_detail(drive_id):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'approved':
        flash('This drive is not available.', 'warning')
        return redirect(url_for('student.browse_drives'))

    already_applied = Application.query.filter_by(
        student_id=student.id, drive_id=drive.id
    ).first()

    return render_template('student/drive_detail.html',
                           drive=drive,
                           student=student,
                           already_applied=already_applied)


@student_bp.route('/drive/<int:drive_id>/apply', methods=['POST'])
@student_required
def apply_drive(drive_id):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'approved':
        flash('This drive is not accepting applications.', 'warning')
        return redirect(url_for('student.browse_drives'))

    if drive.application_deadline < date.today():
        flash('Application deadline has passed.', 'danger')
        return redirect(url_for('student.browse_drives'))

    existing = Application.query.filter_by(
        student_id=student.id, drive_id=drive.id
    ).first()
    if existing:
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('student.drive_detail', drive_id=drive.id))

    if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
        flash(f'You do not meet the minimum CGPA requirement ({drive.min_cgpa}).', 'danger')
        return redirect(url_for('student.drive_detail', drive_id=drive.id))

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student.my_applications'))


@student_bp.route('/applications')
@student_required
def my_applications():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    applications = (
        Application.query
        .filter_by(student_id=student.id)
        .order_by(Application.applied_date.desc())
        .all()
    )
    return render_template('student/my_applications.html',
                           applications=applications,
                           student=student)


@student_bp.route('/history')
@student_required
def history():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    applications = (
        Application.query
        .filter_by(student_id=student.id)
        .filter(Application.status.in_(['Selected', 'Rejected']))
        .order_by(Application.applied_date.desc())
        .all()
    )
    return render_template('student/history.html',
                           applications=applications,
                           student=student)
