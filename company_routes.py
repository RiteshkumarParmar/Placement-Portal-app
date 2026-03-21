from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, CompanyProfile, PlacementDrive, Application, StudentProfile
from functools import wraps
from datetime import datetime

company_bp = Blueprint('company', __name__, template_folder='templates')


def company_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'company':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if not company or company.approval_status != 'approved':
            flash('Your company is not approved yet.', 'warning')
            return redirect(url_for('index'))
        if company.is_blacklisted:
            flash('Your company has been blacklisted.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@company_bp.route('/dashboard')
@company_required
def dashboard():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    total_applicants = 0
    for drive in drives:
        total_applicants += Application.query.filter_by(drive_id=drive.id).count()

    active_drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').count()
    pending_drives = PlacementDrive.query.filter_by(company_id=company.id, status='pending').count()

    return render_template('company/dashboard.html',
                           company=company,
                           drives=drives,
                           total_applicants=total_applicants,
                           active_drives=active_drives,
                           pending_drives=pending_drives)


@company_bp.route('/profile', methods=['GET', 'POST'])
@company_required
def profile():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        company.company_name = request.form.get('company_name', '').strip()
        company.hr_name = request.form.get('hr_name', '').strip()
        company.hr_email = request.form.get('hr_email', '').strip()
        company.hr_phone = request.form.get('hr_phone', '').strip()
        company.website = request.form.get('website', '').strip()
        company.industry = request.form.get('industry', '').strip()
        company.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('company.profile'))

    return render_template('company/profile.html', company=company)


@company_bp.route('/drive/create', methods=['GET', 'POST'])
@company_required
def create_drive():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        job_description = request.form.get('job_description', '').strip()
        job_type = request.form.get('job_type', '').strip()
        location = request.form.get('location', '').strip()
        salary_package = request.form.get('salary_package', '').strip()
        eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
        min_cgpa = request.form.get('min_cgpa', '0')
        departments_allowed = request.form.get('departments_allowed', '').strip()
        deadline_str = request.form.get('application_deadline', '')

        if not job_title or not job_description or not deadline_str:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('company.create_drive'))

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid deadline format.', 'danger')
            return redirect(url_for('company.create_drive'))

        drive = PlacementDrive(
            company_id=company.id,
            job_title=job_title,
            job_description=job_description,
            job_type=job_type,
            location=location,
            salary_package=salary_package,
            eligibility_criteria=eligibility_criteria,
            min_cgpa=float(min_cgpa) if min_cgpa else 0.0,
            departments_allowed=departments_allowed,
            application_deadline=deadline,
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        flash('Placement drive created! It will be visible after admin approval.', 'success')
        return redirect(url_for('company.my_drives'))

    return render_template('company/create_drive.html')


@company_bp.route('/drives')
@company_required
def my_drives():
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    return render_template('company/my_drives.html', drives=drives)


@company_bp.route('/drive/<int:drive_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_drive(drive_id):
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != company.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.my_drives'))

    if request.method == 'POST':
        drive.job_title = request.form.get('job_title', '').strip()
        drive.job_description = request.form.get('job_description', '').strip()
        drive.job_type = request.form.get('job_type', '').strip()
        drive.location = request.form.get('location', '').strip()
        drive.salary_package = request.form.get('salary_package', '').strip()
        drive.eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
        drive.min_cgpa = float(request.form.get('min_cgpa', '0') or '0')
        drive.departments_allowed = request.form.get('departments_allowed', '').strip()

        deadline_str = request.form.get('application_deadline', '')
        if deadline_str:
            try:
                drive.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid deadline format.', 'danger')
                return redirect(url_for('company.edit_drive', drive_id=drive.id))

        db.session.commit()
        flash('Drive updated successfully.', 'success')
        return redirect(url_for('company.my_drives'))

    return render_template('company/edit_drive.html', drive=drive)


@company_bp.route('/drive/<int:drive_id>/delete', methods=['POST'])
@company_required
def delete_drive(drive_id):
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != company.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.my_drives'))

    Application.query.filter_by(drive_id=drive.id).delete()
    db.session.delete(drive)
    db.session.commit()
    flash('Drive deleted successfully.', 'success')
    return redirect(url_for('company.my_drives'))


@company_bp.route('/drive/<int:drive_id>/close', methods=['POST'])
@company_required
def close_drive(drive_id):
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != company.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.my_drives'))

    drive.status = 'closed'
    db.session.commit()
    flash('Drive closed successfully.', 'info')
    return redirect(url_for('company.my_drives'))


@company_bp.route('/drive/<int:drive_id>/applicants')
@company_required
def view_applicants(drive_id):
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != company.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.my_drives'))

    applications = Application.query.filter_by(drive_id=drive.id).order_by(Application.applied_date.desc()).all()
    return render_template('company/applicants.html', drive=drive, applications=applications)


@company_bp.route('/application/<int:app_id>/status', methods=['POST'])
@company_required
def update_application_status(app_id):
    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    application = Application.query.get_or_404(app_id)
    drive = PlacementDrive.query.get(application.drive_id)

    if not drive or drive.company_id != company.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('company.my_drives'))

    new_status = request.form.get('status', '')
    remarks = request.form.get('remarks', '').strip()

    if new_status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        application.status = new_status
        application.remarks = remarks
        db.session.commit()
        flash(f'Application status updated to {new_status}.', 'success')

    return redirect(url_for('company.view_applicants', drive_id=drive.id))
