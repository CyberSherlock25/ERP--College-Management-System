# College ERP — College Management System

A complete, open-source College ERP (Enterprise Resource Planning) web application built with Django. This repository contains the source for a role-based system for administrators, teachers and students — including timetables, attendance, exams, fees, notifications and basic financial workflows.

## Contents
- Features overview
- Quick developer setup
- Project structure
- Troubleshooting & support

---

## Key Features
- Role-based dashboards for Students, Teachers and Administrators
- Timetable management and teacher timetable view
- Attendance recording and reports
- Exam scheduling and results entry
- Fee management, transaction history and receipts
- Notification/announcement system

## Technology
- Python 3.10+
- Django (project uses Django apps laid out under `college_erp_system/`)
- SQLite for development (configurable to PostgreSQL/MySQL in production)
- Bootstrap 5 for frontend layout

## Quick start (development)
1. Clone the repository:
   git clone <repo-url>
   cd ERP--College-Management-System/college_erp_system
2. Create & activate a virtualenv (recommended):
   python3 -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Apply migrations and create a superuser:
   python manage.py migrate
   python manage.py createsuperuser
5. (Optional) Create sample data if available:
   python manage.py create_sample_data
6. Run the dev server:
   python manage.py runserver

Open http://127.0.0.1:8000/ in your browser and sign in with the superuser.

## Project layout
- `college_erp/` — Django project settings and URL routing
- `accounts/`, `academics/`, `students/`, `teachers/`, `administration/` — main Django apps
- `templates/` — shared HTML templates
- `static/` and `media/` — static assets and uploaded files

## Troubleshooting
- If Django isn't found, activate your virtualenv and run `pip install -r requirements.txt`.
- If you run into template or static file issues, run `python manage.py collectstatic --noinput` (for production setups) and confirm template names/paths.

## Contributing
Feel free to open issues or pull requests. If you make changes, please add a brief changelog entry (or update `IMPLEMENTATION_SUMMARY.md`).

## License & notes
Check `setup.py` and root project metadata for licensing information. This repo contains development/demo configuration (SQLite, DEBUG settings). Before production deployment, update settings and secrets appropriately.

---

If anything on this README should be further polished (add images, badges, or more detailed run instructions), tell me what to include and I’ll update it.
