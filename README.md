# PlaceHub - Campus Placement Portal

A full-featured web application for managing campus recruitment activities between institutes, companies, and students. Built with Flask, Jinja2, Bootstrap 5, and SQLite.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation Guide](#installation-guide)
- [Running the Application](#running-the-application)
- [Default Admin Credentials](#default-admin-credentials)
- [Usage Guide](#usage-guide)
  - [Step 1 — Register a Student](#step-1--register-a-student)
  - [Step 2 — Register a Company](#step-2--register-a-company)
  - [Step 3 — Admin Approves the Company](#step-3--admin-approves-the-company)
  - [Step 4 — Company Creates a Placement Drive](#step-4--company-creates-a-placement-drive)
  - [Step 5 — Admin Approves the Drive](#step-5--admin-approves-the-drive)
  - [Step 6 — Student Applies for the Drive](#step-6--student-applies-for-the-drive)
  - [Step 7 — Company Reviews & Updates Status](#step-7--company-reviews--updates-status)
  - [Step 8 — Student Checks Results](#step-8--student-checks-results)
  - [Step 9 — Admin Monitors Everything](#step-9--admin-monitors-everything)
- [Application Flow Diagram](#application-flow-diagram)
- [API Endpoints](#api-endpoints)
- [Screenshots Reference](#screenshots-reference)

---

## Overview

PlaceHub is a placement portal that streamlines the campus recruitment process. It provides three distinct roles:

- **Admin (Institute)** — The superuser who manages the entire placement process.
- **Company** — Organizations that register, create placement drives, and recruit students.
- **Student** — Users who browse drives, apply for positions, and track their placement status.

---

## Features

### Admin (Institute Placement Cell)
- Pre-seeded admin account (no registration needed)
- Dashboard with real-time statistics (total students, companies, drives, applications)
- Approve or reject company registrations
- Approve or reject placement drives
- Search students by name, roll number, or phone
- Search companies by name
- Blacklist, deactivate, or delete student and company accounts
- View all applications with status filtering
- View complete historical placement data

### Company
- Self-registration with admin approval workflow
- Company profile management (HR contact, industry, website, description)
- Create placement drives (job postings) — pending admin approval
- Edit, close, or delete placement drives
- View student applications per drive
- Update application status (Applied → Shortlisted → Selected / Rejected)
- Add remarks to applications

### Student
- Self-registration and login
- Profile management with resume upload (PDF, DOC, DOCX)
- Browse approved placement drives with search functionality
- View detailed drive information with eligibility check
- One-click application to drives
- Track application status in real-time
- View placement history (finalized results)

### Core Business Rules
- Duplicate applications prevented (one application per student per drive)
- Only admin-approved companies can create placement drives
- Only admin-approved drives are visible to students
- CGPA eligibility enforcement before application submission
- Application deadline enforcement
- Blacklisted/deactivated accounts are blocked from login

---

## Tech Stack

| Component     | Technology                              |
|---------------|----------------------------------------|
| Backend       | Flask 3.1.0 (Python)                   |
| Templating    | Jinja2                                 |
| Frontend      | HTML5, CSS3, Bootstrap 5.3.2           |
| Icons         | Bootstrap Icons 1.11.3                 |
| Database      | SQLite (via Flask-SQLAlchemy 3.1.1)    |
| Auth          | Flask-Login 0.6.3                      |
| Password Hash | Werkzeug (pbkdf2:sha256)               |

---

## Project Structure

```
Ash-Proj/
├── app.py                          # Main application, config, auth routes, admin seeding
├── models.py                       # SQLAlchemy database models
├── admin_routes.py                 # Admin blueprint — manage companies, students, drives
├── company_routes.py               # Company blueprint — profile, drives, applicants
├── student_routes.py               # Student blueprint — browse, apply, track
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── static/
│   └── css/
│       └── style.css               # Custom CSS (gradient navbar, card hover, form styling)
│
├── templates/
│   ├── base.html                   # Base layout with role-aware navbar
│   ├── index.html                  # Landing page
│   │
│   ├── auth/
│   │   ├── login.html              # Login form (all roles)
│   │   ├── register_student.html   # Student registration form
│   │   └── register_company.html   # Company registration form
│   │
│   ├── admin/
│   │   ├── dashboard.html          # Admin dashboard with stats
│   │   ├── companies.html          # Company list with search & filter
│   │   ├── company_detail.html     # Single company details + drives
│   │   ├── students.html           # Student list with search
│   │   ├── student_detail.html     # Single student details + applications
│   │   ├── drives.html             # All drives with status filter
│   │   ├── drive_detail.html       # Single drive details + applicants
│   │   └── applications.html       # All applications with status filter
│   │
│   ├── company/
│   │   ├── dashboard.html          # Company dashboard with stats
│   │   ├── profile.html            # Edit company profile
│   │   ├── create_drive.html       # Create new placement drive
│   │   ├── edit_drive.html         # Edit existing drive
│   │   ├── my_drives.html          # List of company's drives
│   │   └── applicants.html         # View & manage applicants per drive
│   │
│   └── student/
│       ├── dashboard.html          # Student dashboard with stats
│       ├── profile.html            # Edit student profile + resume upload
│       ├── browse_drives.html      # Browse approved drives with search
│       ├── drive_detail.html       # Drive details + apply button
│       ├── my_applications.html    # Track all applications
│       └── history.html            # Finalized placement history
│
├── uploads/                        # Resume file uploads (auto-created)
└── instance/
    └── placement_portal.db         # SQLite database (auto-created)
```

---

## Database Schema

### ER Diagram (Textual)

```
┌──────────────┐       ┌──────────────────┐       ┌───────────────────┐
│     User     │       │  StudentProfile   │       │  CompanyProfile   │
├──────────────┤       ├──────────────────┤       ├───────────────────┤
│ id (PK)      │──1:1──│ id (PK)          │       │ id (PK)           │
│ email        │       │ user_id (FK)     │       │ user_id (FK)      │──1:1──┐
│ password_hash│       │ name             │       │ company_name      │       │
│ role         │       │ roll_number (UQ) │       │ hr_name           │       │
│ is_active    │       │ phone            │       │ hr_email          │     User
│ created_at   │       │ department       │       │ hr_phone          │
└──────────────┘       │ cgpa             │       │ website           │
                       │ resume_path      │       │ industry          │
                       │ skills           │       │ description       │
                       │ about            │       │ approval_status   │
                       │ graduation_year  │       │ is_blacklisted    │
                       │ is_blacklisted   │       └───────┬───────────┘
                       └───────┬──────────┘               │
                               │                          │ 1:N
                               │                          ▼
                               │               ┌───────────────────┐
                               │               │  PlacementDrive   │
                               │               ├───────────────────┤
                               │               │ id (PK)           │
                               │               │ company_id (FK)   │
                               │               │ job_title         │
                               │               │ job_description   │
                               │               │ job_type          │
                               │               │ location          │
                               │               │ salary_package    │
                               │               │ eligibility       │
                               │               │ min_cgpa          │
                               │               │ departments       │
                               │               │ deadline          │
                               │               │ status            │
                               │               │ created_at        │
                               │               └───────┬───────────┘
                               │                       │ 1:N
                               │ 1:N                   │
                               ▼                       ▼
                       ┌───────────────────────────────────┐
                       │           Application             │
                       ├───────────────────────────────────┤
                       │ id (PK)                           │
                       │ student_id (FK → StudentProfile)  │
                       │ drive_id (FK → PlacementDrive)    │
                       │ applied_date                      │
                       │ status                            │
                       │ remarks                           │
                       │ UNIQUE(student_id, drive_id)      │
                       └───────────────────────────────────┘
```

### Table Details

| Table            | Key Columns                                                         |
|------------------|---------------------------------------------------------------------|
| `user`           | id, email, password_hash, role (admin/company/student), is_active   |
| `student_profile`| id, user_id, name, roll_number, phone, department, cgpa, resume     |
| `company_profile`| id, user_id, company_name, hr_name, hr_email, approval_status       |
| `placement_drive`| id, company_id, job_title, job_type, location, salary, deadline, status |
| `application`    | id, student_id, drive_id, applied_date, status, remarks             |

### Status Values

| Entity      | Possible Status Values                    |
|-------------|------------------------------------------|
| Company     | `pending`, `approved`, `rejected`         |
| Drive       | `pending`, `approved`, `closed`, `rejected` |
| Application | `Applied`, `Shortlisted`, `Selected`, `Rejected` |

---

## Installation Guide

### Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Step-by-Step Installation

1. **Clone or download the project**

   ```bash
   cd /path/to/your/directory
   # If using git:
   # git clone <repository-url>
   # Or simply copy the project folder
   ```

2. **Navigate to the project directory**

   ```bash
   cd Ash-Proj
   ```

3. **(Recommended) Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # macOS / Linux
   # venv\Scripts\activate          # Windows
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - Flask 3.1.0
   - Flask-SQLAlchemy 3.1.1
   - Flask-Login 0.6.3
   - Werkzeug 3.1.3

5. **Run the application**

   ```bash
   python3 app.py
   ```

6. **Open in browser**

   Navigate to: **http://127.0.0.1:5000**

> The SQLite database (`instance/placement_portal.db`) and uploads folder are created automatically on first run. A default admin user is also seeded automatically.

---

## Running the Application

```bash
# Start the server
python3 app.py

# The app runs at http://127.0.0.1:5000
# Press Ctrl+C to stop the server
```

To reset the database and start fresh:

```bash
rm -f instance/placement_portal.db
python3 app.py
```

---

## Default Admin Credentials

| Field    | Value                  |
|----------|------------------------|
| Email    | `admin@placement.edu`  |
| Password | `admin123`             |

> The admin account is created automatically when the application starts for the first time. There is no admin registration — admin must pre-exist in the database.

---

## Usage Guide

Below is the complete workflow to test every feature of the application.

### Step 1 — Register a Student

1. Open **http://127.0.0.1:5000/register/student**
2. Fill in the registration form:
   - Full Name: `Amit Kumar`
   - Roll Number: `21CS001`
   - Email: `rajat@student.com`
   - Password: `student123`
   - Confirm Password: `student123`
   - Phone: `9876543210`
   - Department: `Computer Science`
   - CGPA: `8.5`
   - Graduation Year: `2026`
3. Click **Register**
4. You will be redirected to the login page with a success message

### Step 2 — Register a Company

1. Open **http://127.0.0.1:5000/register/company**
2. Fill in the registration form:
   - Company Name: `Google India`
   - Login Email: `google@company.com`
   - Password: `company123`
   - Confirm Password: `company123`
   - HR Contact Name: `Priya Sharma`
   - HR Email: `priya@google.com`
   - HR Phone: `9988776655`
   - Industry: `IT/Software`
   - Website: `https://google.com`
   - Description: `Leading technology company`
3. Click **Submit Registration**
4. You will see: *"Please wait for admin approval before logging in."*

> **Important:** Companies cannot log in until the admin approves their registration.

### Step 3 — Admin Approves the Company

1. Go to **http://127.0.0.1:5000/login**
2. Log in as admin:
   - Email: `admin@placement.edu`
   - Password: `admin123`
3. You land on the **Admin Dashboard** showing stats
4. Click **Companies** in the top navbar
5. Find `Google India` with a yellow **Pending** badge
6. Click the **green checkmark (✓)** button to approve
7. The badge changes to green **Approved**
8. Click **Logout** (top-right corner)

### Step 4 — Company Creates a Placement Drive

1. Log in as the company:
   - Email: `google@company.com`
   - Password: `company123`
2. You land on the **Company Dashboard**
3. Click **New Drive** in the navbar (or the "Create New Drive" button)
4. Fill in the drive details:
   - Job Title: `Software Engineer`
   - Job Description: `Build scalable distributed systems at Google`
   - Job Type: `Full-time`
   - Location: `Bangalore`
   - Salary Package: `25 LPA`
   - Eligibility Criteria: `No active backlogs, B.Tech CS/IT only`
   - Minimum CGPA: `7.0`
   - Departments Allowed: `CS, IT`
   - Application Deadline: pick a future date (e.g., `2026-04-01`)
5. Click **Create Drive**
6. The drive appears with a **Pending** status (needs admin approval)
7. Click **Logout**

> **Note:** Companies can only create drives after admin approval. Drives themselves also require admin approval before students can see them.

### Step 5 — Admin Approves the Drive

1. Log in as admin (`admin@placement.edu` / `admin123`)
2. Click **Drives** in the navbar
3. Find `Software Engineer` with a **Pending** badge
4. Click the **green checkmark (✓)** button to approve
5. The drive is now visible to students
6. Click **Logout**

### Step 6 — Student Applies for the Drive

1. Log in as the student:
   - Email: `rajat@student.com`
   - Password: `student123`
2. You land on the **Student Dashboard** showing the approved drive
3. Click **Browse Drives** in the navbar to see all available drives
4. Click **View Details** on the `Software Engineer` drive
5. Review the job description, eligibility, and your CGPA match
6. Click **Apply Now**
7. You see a success message: *"Application submitted successfully!"*
8. Go to **Applications** in the navbar to see your application with status **Applied**

> **Note:** You cannot apply to the same drive twice. The system enforces this automatically.

### Step 7 — Company Reviews & Updates Status

1. Log out and log in as company (`google@company.com` / `company123`)
2. On the Dashboard, you see **1 applicant** on the drive
3. Click the **people icon** next to the drive (or go to My Drives → Applicants)
4. You see the student's profile: name, roll number, CGPA, skills, phone
5. Use the **Update Status** dropdown to change from `Applied` to `Shortlisted`
6. Optionally add remarks like `Strong profile, proceed to interview`
7. Click the **blue check** button to save
8. Later, update to `Selected` or `Rejected` to finalize

### Step 8 — Student Checks Results

1. Log out and log in as student (`rajat@student.com` / `student123`)
2. Go to **Applications** — the status now shows **Shortlisted** / **Selected**
3. Click **View History** to see finalized placements (Selected or Rejected only)

### Step 9 — Admin Monitors Everything

1. Log in as admin (`admin@placement.edu` / `admin123`)
2. **Dashboard** — See all updated counts and recent applications
3. **Students** — Search by name/roll/phone, blacklist or deactivate accounts
4. **Companies** — Search by name, blacklist or delete companies
5. **Drives** — Filter by status (pending/approved/closed/rejected)
6. **Applications** — Filter by status (Applied/Shortlisted/Selected/Rejected), see complete history

---

## Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PLACEMENT PORTAL FLOW                        │
└─────────────────────────────────────────────────────────────────────┘

  Student Registers ──→ Can Login Immediately
                              │
                              ▼
                       Student Dashboard
                       (Browse & Apply)

  Company Registers ──→ Status: PENDING ──→ Admin Approves ──→ Can Login
                                                                  │
                                                                  ▼
                                                          Company Dashboard
                                                          (Create Drives)
                                                                  │
                                                                  ▼
                                                         Drive Status: PENDING
                                                                  │
                                                                  ▼
                                                          Admin Approves Drive
                                                                  │
                                                                  ▼
                                                        Drive Visible to Students
                                                                  │
                                                                  ▼
                                                         Student Applies
                                                                  │
                                                                  ▼
                                                     Application Status: APPLIED
                                                                  │
                                                                  ▼
                                                    Company Reviews Application
                                                                  │
                                                    ┌─────────────┼─────────────┐
                                                    ▼             ▼             ▼
                                              SHORTLISTED    SELECTED      REJECTED
```

---

## API Endpoints

### Public Routes

| Method | URL                  | Description              |
|--------|----------------------|--------------------------|
| GET    | `/`                  | Landing page             |
| GET/POST | `/login`          | Login form               |
| GET/POST | `/register/student`| Student registration    |
| GET/POST | `/register/company`| Company registration    |
| GET    | `/logout`            | Logout                   |

### Admin Routes (`/admin/...`)

| Method | URL                                  | Description                    |
|--------|--------------------------------------|--------------------------------|
| GET    | `/admin/dashboard`                   | Admin dashboard with stats     |
| GET    | `/admin/companies`                   | List companies (search/filter) |
| GET    | `/admin/company/<id>`                | Company details                |
| POST   | `/admin/company/<id>/approve`        | Approve company                |
| POST   | `/admin/company/<id>/reject`         | Reject company                 |
| POST   | `/admin/company/<id>/blacklist`      | Toggle blacklist               |
| POST   | `/admin/company/<id>/delete`         | Delete company                 |
| GET    | `/admin/students`                    | List students (search)         |
| GET    | `/admin/student/<id>`                | Student details                |
| POST   | `/admin/student/<id>/blacklist`      | Toggle blacklist               |
| POST   | `/admin/student/<id>/deactivate`     | Toggle active status           |
| POST   | `/admin/student/<id>/delete`         | Delete student                 |
| GET    | `/admin/drives`                      | List drives (filter by status) |
| GET    | `/admin/drive/<id>`                  | Drive details                  |
| POST   | `/admin/drive/<id>/approve`          | Approve drive                  |
| POST   | `/admin/drive/<id>/reject`           | Reject drive                   |
| GET    | `/admin/applications`                | List all applications          |

### Company Routes (`/company/...`)

| Method | URL                                  | Description                    |
|--------|--------------------------------------|--------------------------------|
| GET    | `/company/dashboard`                 | Company dashboard              |
| GET/POST | `/company/profile`                | Edit company profile           |
| GET/POST | `/company/drive/create`           | Create new drive               |
| GET    | `/company/drives`                    | List company's drives          |
| GET/POST | `/company/drive/<id>/edit`        | Edit drive                     |
| POST   | `/company/drive/<id>/delete`         | Delete drive                   |
| POST   | `/company/drive/<id>/close`          | Close drive                    |
| GET    | `/company/drive/<id>/applicants`     | View applicants                |
| POST   | `/company/application/<id>/status`   | Update application status      |

### Student Routes (`/student/...`)

| Method | URL                                  | Description                    |
|--------|--------------------------------------|--------------------------------|
| GET    | `/student/dashboard`                 | Student dashboard              |
| GET/POST | `/student/profile`                | Edit profile + upload resume   |
| GET    | `/student/drives`                    | Browse approved drives         |
| GET    | `/student/drive/<id>`                | Drive details                  |
| POST   | `/student/drive/<id>/apply`          | Apply for a drive              |
| GET    | `/student/applications`              | View all applications          |
| GET    | `/student/history`                   | View placement history         |

---

## Screenshots Reference

| Screen                  | URL                            |
|-------------------------|--------------------------------|
| Landing Page            | `/`                            |
| Login                   | `/login`                       |
| Student Registration    | `/register/student`            |
| Company Registration    | `/register/company`            |
| Admin Dashboard         | `/admin/dashboard`             |
| Company Dashboard       | `/company/dashboard`           |
| Student Dashboard       | `/student/dashboard`           |
| Browse Drives           | `/student/drives`              |
| Drive Detail            | `/student/drive/1`             |

---

## Troubleshooting

| Problem                           | Solution                                              |
|-----------------------------------|-------------------------------------------------------|
| `Port 5000 in use`               | Run `lsof -ti:5000 \| xargs kill -9` then restart    |
| `Invalid email or password`       | Verify you're using the correct credentials           |
| `Company pending approval`        | Log in as admin and approve the company first         |
| `No drives visible to student`    | Ensure the drive is approved by admin                 |
| `Cannot apply — CGPA too low`     | Update student CGPA in profile to meet minimum        |
| `Database issues`                 | Delete `instance/placement_portal.db` and restart     |
| `hashlib scrypt error`            | Already fixed — uses `pbkdf2:sha256` method           |