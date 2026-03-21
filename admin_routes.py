from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from functools import wraps

admin_bp = Blueprint('admin', __name__, template_folder='templates')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    pending_companies = CompanyProfile.query.filter_by(approval_status='pending').count()
    pending_drives = PlacementDrive.query.filter_by(status='pending').count()
    approved_companies = CompanyProfile.query.filter_by(approval_status='approved').count()
    recent_applications = (
        Application.query
        .order_by(Application.applied_date.desc())
        .limit(10)
        .all()
    )
    selected_count = Application.query.filter_by(status='Selected').count()
    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_companies=total_companies,
                           total_drives=total_drives,
                           total_applications=total_applications,
                           pending_companies=pending_companies,
                           pending_drives=pending_drives,
                           approved_companies=approved_companies,
                           recent_applications=recent_applications,
                           selected_count=selected_count)


# ── Company management ────────────────────────────────────────────────

@admin_bp.route('/companies')
@admin_required
def companies():
    status_filter = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()

    query = CompanyProfile.query
    if status_filter != 'all':
        query = query.filter_by(approval_status=status_filter)
    if search:
        query = query.filter(CompanyProfile.company_name.ilike(f'%{search}%'))

    companies_list = query.order_by(CompanyProfile.id.desc()).all()
    return render_template('admin/companies.html',
                           companies=companies_list,
                           status_filter=status_filter,
                           search=search)


@admin_bp.route('/company/<int:company_id>')
@admin_required
def company_detail(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    return render_template('admin/company_detail.html', company=company, drives=drives)


@admin_bp.route('/company/<int:company_id>/approve', methods=['POST'])
@admin_required
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    flash(f'{company.company_name} has been approved.', 'success')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/company/<int:company_id>/reject', methods=['POST'])
@admin_required
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'{company.company_name} has been rejected.', 'warning')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/company/<int:company_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    action = 'blacklisted' if company.is_blacklisted else 'unblacklisted'
    flash(f'{company.company_name} has been {action}.', 'info')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/company/<int:company_id>/delete', methods=['POST'])
@admin_required
def delete_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    user = User.query.get(company.user_id)

    for drive in company.drives:
        Application.query.filter_by(drive_id=drive.id).delete()
    PlacementDrive.query.filter_by(company_id=company.id).delete()

    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash('Company and all related data deleted.', 'success')
    return redirect(url_for('admin.companies'))


# ── Student management ────────────────────────────────────────────────

@admin_bp.route('/students')
@admin_required
def students():
    search = request.args.get('q', '').strip()
    query = StudentProfile.query

    if search:
        query = query.filter(
            db.or_(
                StudentProfile.name.ilike(f'%{search}%'),
                StudentProfile.roll_number.ilike(f'%{search}%'),
                StudentProfile.phone.ilike(f'%{search}%')
            )
        )

    students_list = query.order_by(StudentProfile.id.desc()).all()
    return render_template('admin/students.html', students=students_list, search=search)


@admin_bp.route('/student/<int:student_id>')
@admin_required
def student_detail(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    applications = Application.query.filter_by(student_id=student.id).all()
    return render_template('admin/student_detail.html', student=student, applications=applications)


@admin_bp.route('/student/<int:student_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    action = 'blacklisted' if student.is_blacklisted else 'unblacklisted'
    flash(f'{student.name} has been {action}.', 'info')
    return redirect(url_for('admin.students'))


@admin_bp.route('/student/<int:student_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    if user:
        user.is_active_account = not user.is_active_account
        db.session.commit()
        action = 'deactivated' if not user.is_active_account else 'activated'
        flash(f'{student.name} account has been {action}.', 'info')
    return redirect(url_for('admin.students'))


@admin_bp.route('/student/<int:student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    Application.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash('Student and all related data deleted.', 'success')
    return redirect(url_for('admin.students'))


# ── Drive management ──────────────────────────────────────────────────

@admin_bp.route('/drives')
@admin_required
def drives():
    status_filter = request.args.get('status', 'all')
    query = PlacementDrive.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    drives_list = query.order_by(PlacementDrive.created_at.desc()).all()
    return render_template('admin/drives.html', drives=drives_list, status_filter=status_filter)


@admin_bp.route('/drive/<int:drive_id>')
@admin_required
def drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template('admin/drive_detail.html', drive=drive, applications=applications)


@admin_bp.route('/drive/<int:drive_id>/approve', methods=['POST'])
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been approved.', 'success')
    return redirect(url_for('admin.drives'))


@admin_bp.route('/drive/<int:drive_id>/reject', methods=['POST'])
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" has been rejected.', 'warning')
    return redirect(url_for('admin.drives'))


# ── Applications view ─────────────────────────────────────────────────

@admin_bp.route('/applications')
@admin_required
def applications():
    status_filter = request.args.get('status', 'all')
    query = Application.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    applications_list = query.order_by(Application.applied_date.desc()).all()
    return render_template('admin/applications.html',
                           applications=applications_list,
                           status_filter=status_filter)
