# Quick Start Guide - Teacher Features

## Prerequisites
Ensure you're in the correct directory:
```powershell
cd E:\MIT\Python\ERP--College-Management-System\college_erp_system
```

## Step 1: Add Timetable Image
Place your timetable image at:
```
E:\MIT\Python\ERP--College-Management-System\college_erp_system\static\images\timetable.png
```

Supported formats: PNG, JPG, WebP
Recommended size: 1200x800 pixels

## Step 2: Apply Migrations (if any new migrations exist)
```powershell
python manage.py migrate
```

## Step 3: Collect Static Files
```powershell
python manage.py collectstatic --noinput
```

## Step 4: Run Development Server
```powershell
python manage.py runserver
```

Your application will be available at: **http://127.0.0.1:8000/**

## Access the Features

### Teacher Dashboard
- URL: `http://127.0.0.1:8000/teachers/dashboard/`
- Login as a teacher user

### Schedule Exam
- URL: `http://127.0.0.1:8000/teachers/exams/`
- Select subjects and enter exam details
- Create exam records

### View Timetable
- URL: `http://127.0.0.1:8000/teachers/timetable/`
- View organized timetable grid
- See timetable image
- Switch between academic years

## Commands Summary

| Purpose | Command |
|---------|---------|
| Run migrations | `python manage.py migrate` |
| Collect static files | `python manage.py collectstatic --noinput` |
| Start server | `python manage.py runserver` |
| Create superuser | `python manage.py createsuperuser` |
| Django shell | `python manage.py shell` |
| Check syntax | `python manage.py check` |

## Troubleshooting

**Port already in use?**
```powershell
python manage.py runserver 8001
```

**Clear cache?**
```powershell
python manage.py clear_cache  # if using cache
```

**Reset database (DEV ONLY)?**
```powershell
# Delete db.sqlite3 and
python manage.py migrate
```

## File Checklist
- [x] teachers/views.py - Updated with 3 new views
- [x] teachers/urls.py - Updated with new routes
- [x] templates/teachers/exam_select.html - Created
- [x] templates/teachers/timetable.html - Updated
- [x] static/images/ - Directory created
- [ ] static/images/timetable.png - **NEED TO ADD YOUR IMAGE**

## Features Added

### Exam Scheduling
- Teachers can schedule exams for multiple subjects
- Form-based interface with validation
- Auto-creates exam records in database
- Success notifications

### Enhanced Timetable
- Grid view of teaching schedule
- Organized by day and time slot
- Timetable image display
- Summary table view
- Academic year selector

## Need Help?
See `TEACHER_FEATURES_SETUP.md` for detailed documentation.
