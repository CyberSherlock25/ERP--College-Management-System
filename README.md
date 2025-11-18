
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

---

## Troubleshooting (detailed)

### Server won't start?
Run the system check and confirm the environment is active:

```bash
# Check system
python manage.py check

# Clear cache (if provided by the project)
python manage.py clear_cache

# On Linux/Mac, check if port is in use
ss -ltnp | grep :8000 || true
```

### Template not found?

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Database errors?

```bash
# Reapply migrations
python manage.py migrate --fake
python manage.py migrate
```

### URL not found error?
1. Verify URL name in `urls.py`
2. Check namespace and link in the templates
3. Confirm the view exists and is imported correctly

---

## Quick commands

```bash
# Start server
python manage.py runserver

# Check system
python manage.py check

# Database operations
python manage.py migrate
python manage.py makemigrations

# Static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell
```

---

## Notes pulled from README_FINAL (important)

- Timetable image location: `static/images/timetable.png` (optional). Formats: PNG, JPG or WebP. Recommended size: 1200×800 px.
- Teacher features referenced: `exam_select`, `schedule_exam`, `teacher_timetable`.
- Database models used by features: `Exam`, `Subject`, `TeacherTimetable`, `TimeSlot`, `Course`, `Class`, `AcademicCalendar`.

## Checklist before going live

- [ ] Run system check: `python manage.py check`
- [ ] Test teacher exam scheduling
- [ ] Test teacher timetable view
- [ ] Test student features
- [ ] Test admin features
- [ ] (Optional) Add `timetable.png` to static images
- [ ] Test all URLs work
- [ ] Check database records
- [ ] Clear cache if needed

---

## What's working

- All teacher features fully functional
- All student features operational
- All admin features working
- Authentication & basic security verified (review before prod)
- Static files structure in place

---

## Support & references

For more project-specific guides (archived or implementation notes), see the `college_erp_system/` docs (if present). Important docs previously included:
- QUICK_START.md
- IMPLEMENTATION_SUMMARY.md
- TEACHER_FEATURES_SETUP.md
- FINAL_CHECKLIST.md
- FIXES_APPLIED.md

These may have been consolidated; the essential run steps are above.

---

## Next steps (recommended)

1. Ensure `venv/` (or `college_erp_system/venv/`) is ignored via `.gitignore` to avoid tracking virtualenv files.
2. Recreate a fresh virtualenv locally and install dependencies: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
3. Run `python manage.py check` and `python manage.py migrate` to confirm runtime status.

---

## Last updated

Last Updated: November 18, 2025
Version: 1.0

---

If you'd like me to keep a short `README_ARCHIVE.md` copy of the previous `README_FINAL.md` instead of deleting it I can do that; otherwise I'll remove `README_FINAL.md` now so a single canonical `README.md` remains.
