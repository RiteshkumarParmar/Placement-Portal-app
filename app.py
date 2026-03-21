import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'placement-portal-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Register blueprints ──────────────────────────────────────────────
from admin_routes import admin_bp
from company_routes import company_bp
from student_routes import student_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(company_bp, url_prefix='/company')
app.register_blueprint(student_bp, url_prefix='/student')


# ── Public routes ─────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        if not user.is_active_account:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('login'))

        if user.role == 'company':
            company = CompanyProfile.query.filter_by(user_id=user.id).first()
            if company and company.approval_status == 'pending':
                flash('Your company registration is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            if company and company.approval_status == 'rejected':
                flash('Your company registration was rejected by admin.', 'danger')
                return redirect(url_for('login'))
            if company and company.is_blacklisted:
                flash('Your company has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('login'))

        if user.role == 'student':
            student = StudentProfile.query.filter_by(user_id=user.id).first()
            if student and student.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin.', 'danger')
                return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully.', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))

    return render_template('auth/login.html')


@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        cgpa = request.form.get('cgpa', '0')
        graduation_year = request.form.get('graduation_year', '')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register_student'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register_student'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register_student'))

        if StudentProfile.query.filter_by(roll_number=roll_number).first():
            flash('Roll number already registered.', 'danger')
            return redirect(url_for('register_student'))

        user = User(email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        profile = StudentProfile(
            user_id=user.id,
            name=name,
            roll_number=roll_number,
            phone=phone,
            department=department,
            cgpa=float(cgpa) if cgpa else 0.0,
            graduation_year=int(graduation_year) if graduation_year else None
        )
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register_student.html')


@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        company_name = request.form.get('company_name', '').strip()
        hr_name = request.form.get('hr_name', '').strip()
        hr_email = request.form.get('hr_email', '').strip()
        hr_phone = request.form.get('hr_phone', '').strip()
        website = request.form.get('website', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register_company'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register_company'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register_company'))

        user = User(email=email, role='company')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        profile = CompanyProfile(
            user_id=user.id,
            company_name=company_name,
            hr_name=hr_name,
            hr_email=hr_email,
            hr_phone=hr_phone,
            website=website,
            industry=industry,
            description=description,
            approval_status='pending'
        )
        db.session.add(profile)
        db.session.commit()

        flash('Registration submitted! Please wait for admin approval before logging in.', 'info')
        return redirect(url_for('login'))

    return render_template('auth/register_company.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ── Seed admin user ──────────────────────────────────────────────────

def seed_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(email='admin@placement.edu', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


# ── Run ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True, port=5000)
