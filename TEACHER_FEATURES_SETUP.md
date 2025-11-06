# Teacher Exam Scheduling & Timetable Features - Setup Guide

## Overview
This document provides instructions for implementing and running the new teacher features:
1. **Exam Scheduling** (`exam_select` and `schedule_exam` views)
2. **Enhanced Teacher Timetable** (`teacher_timetable` view)

## What Was Added

### 1. New Views (teachers/views.py)
- **`exam_select(request)`**: GET view that displays a form for teachers to select subjects and enter exam details
- **`schedule_exam(request)`**: POST view that creates Exam records for selected subjects
- **`teacher_timetable(request)`**: Enhanced view that organizes teacher timetable in grid format

### 2. URL Routes (teachers/urls.py)
```python
path('exams/', views.exam_select, name='exam_select'),
path('exams/schedule/', views.schedule_exam, name='schedule_exam'),
path('timetable/', views.teacher_timetable, name='timetable'),
```

### 3. Templates
- **teachers/exam_select.html**: Exam scheduling form with:
  - Exam name, type, date, and time
  - Total marks and pass marks
  - Duration (hours and minutes)
  - Instructions field
  - Subject selection (multi-select checkboxes)
  
- **teachers/timetable.html**: Enhanced timetable view with:
  - Grid layout showing days of week vs time slots
  - Timetable image section placeholder
  - Schedule summary table

### 4. Static Files
- Created directory: `static/images/`
- Ready for timetable image placement

## Pre-requisites

Ensure your Django project has:
- Python 3.8+
- Django 3.2+
- All required apps in INSTALLED_APPS:
  - `academics`
  - `teachers`
  - `students`
  - `accounts`
  - `administration`

## Installation & Setup Steps

### Step 1: Files Already Modified
The following files have already been updated:
```
college_erp_system/teachers/views.py      ✓ New views added
college_erp_system/teachers/urls.py       ✓ New routes added
college_erp_system/templates/teachers/exam_select.html    ✓ Created
college_erp_system/templates/teachers/timetable.html      ✓ Updated
college_erp_system/static/images/         ✓ Directory created
```

### Step 2: Add Timetable Image
Place your timetable image file at:
```
college_erp_system/static/images/timetable.png
```

**Image Requirements:**
- Format: PNG, JPG, or WebP
- Recommended size: 1200x800 pixels (responsive)
- File name: `timetable.png` (or update the template path accordingly)

### Step 3: Run Migrations
No new migrations are needed since all models already exist. However, ensure all previous migrations are applied:

```bash
cd college_erp_system
python manage.py migrate
```

### Step 4: Collect Static Files
Collect static files for production-like serving:

```bash
python manage.py collectstatic --noinput
```

### Step 5: Run Development Server
```bash
python manage.py runserver
```

The server will start on `http://127.0.0.1:8000/`

## Features & Usage

### Exam Scheduling (`/teachers/exams/`)

**Access:** Teachers can access exam scheduling via:
1. Navigation menu → Teacher Dashboard → Exams (if added to nav)
2. Direct URL: `/teachers/exams/`

**Form Fields:**
- **Exam Name** (Required): Descriptive name like "Midterm Exam", "Quiz 1"
- **Exam Type** (Required): Select from predefined types (midterm, final, quiz, assignment, project)
- **Date** (Required): Exam date in YYYY-MM-DD format
- **Time** (Required): Exam start time in HH:MM format
- **Total Marks** (Required): Maximum marks for the exam (default: 100)
- **Pass Marks** (Required): Minimum marks to pass (must be ≤ total marks)
- **Duration**: Hours and minutes (default: 1 hour, 0 minutes)
- **Instructions**: Optional exam instructions (e.g., "No calculator allowed")
- **Subjects** (Required): Multi-select checkboxes for subject assignment

**Process:**
1. Teacher selects one or more subjects
2. Fills in exam details
3. Submits form
4. System creates one Exam record per selected subject
5. Success message displayed with count of created exams
6. Redirects to teacher dashboard

**Validation:**
- Exam name cannot be empty
- At least one subject must be selected
- Marks must be positive numbers
- Pass marks cannot exceed total marks
- Date/time must be valid format

### Enhanced Teacher Timetable (`/teachers/timetable/`)

**Access:**
1. Navigation menu → My Timetable
2. Direct URL: `/teachers/timetable/`

**Features:**
- **Academic Year Selector**: Dropdown to view timetables for different academic years
- **Grid View**: 
  - Rows: Time slots (start time to end time)
  - Columns: Days of the week (Monday to Saturday)
  - Cells: Class details including:
    - Course code
    - Course name
    - Class section
    - Room number
- **Timetable Image**: Visual overview section (add your image)
- **Summary Table**: Detailed list view with all schedule information

**Data Displayed:**
- Subject course code and name
- Assigned class
- Room number (or "TBA" if not set)
- Time slot details

## Database Models Used

### Exam Model
```python
- name: CharField(max_length=100)
- exam_type: CharField (midterm, final, quiz, assignment, project)
- subject: ForeignKey(Subject)
- date: DateTimeField
- duration: DurationField
- total_marks: IntegerField
- pass_marks: IntegerField
- instructions: TextField (optional)
- created_by: ForeignKey(User/Teacher)
- created_at: DateTimeField
```

### TeacherTimetable Model
```python
- teacher: ForeignKey(User)
- subject: ForeignKey(Subject)
- time_slot: ForeignKey(TimeSlot)
- room_number: CharField (optional)
- academic_year: CharField
```

### Subject Model
```python
- course: ForeignKey(Course)
- class_assigned: ForeignKey(Class)
- teacher: ForeignKey(User)
- subject_type: CharField (TH, PR, TU)
```

## API Endpoints Summary

| URL | Method | View | Purpose |
|-----|--------|------|---------|
| `/teachers/exams/` | GET | exam_select | Display exam scheduling form |
| `/teachers/exams/schedule/` | POST | schedule_exam | Create exam records |
| `/teachers/timetable/` | GET | teacher_timetable | Display organized timetable |

## Troubleshooting

### Issue: "Access denied" message
**Solution:** Ensure the logged-in user has `is_teacher=True` attribute set.

### Issue: No subjects appear in exam form
**Solution:** 
1. Check if subjects are assigned to the teacher in the Subject model
2. Verify `Subject.teacher` field is set correctly
3. Run in admin panel: filter subjects by teacher

### Issue: Timetable grid appears empty
**Solution:**
1. Ensure TeacherTimetable records exist for the selected academic year
2. Verify TimeSlot records are created in the database
3. Check academic_year parameter matches database records

### Issue: Static image not displaying
**Solution:**
1. Ensure timetable.png is placed in `static/images/` directory
2. Run `python manage.py collectstatic` again
3. Check file permissions
4. Clear browser cache

### Issue: Form validation errors
**Solution:**
1. Ensure all required fields are filled
2. Pass marks ≤ total marks
3. Date format: YYYY-MM-DD
4. Time format: HH:MM (24-hour)

## Testing the Implementation

### Test Exam Scheduling:
```bash
# Login as teacher
# Navigate to /teachers/exams/
# Fill form with:
#   - Exam Name: "Midterm Test"
#   - Type: "midterm"
#   - Date: Future date
#   - Time: 10:00
#   - Marks: 100, Pass: 40
#   - Select 2+ subjects
# Submit and verify success message
# Check Exam records in Django admin
```

### Test Timetable Display:
```bash
# Navigate to /teachers/timetable/
# Verify grid displays correctly
# Try different academic years
# Check image loads properly
# Verify subject details display
```

## File Locations Reference

```
college_erp_system/
├── teachers/
│   ├── views.py              ✓ Updated with 3 new views
│   ├── urls.py               ✓ Updated with new routes
│   └── models.py
├── templates/
│   └── teachers/
│       ├── exam_select.html  ✓ Created
│       ├── timetable.html    ✓ Updated
│       ├── dashboard.html
│       └── attendance_*.html
├── static/
│   └── images/
│       └── timetable.png     ← ADD YOUR IMAGE HERE
├── academics/
│   ├── models.py             (Exam, Subject, TeacherTimetable, TimeSlot)
│   └── templatetags/
│       └── timetable_filters.py
└── manage.py
```

## Next Steps (Optional Enhancements)

1. **Add exam editing/deletion**: Create update and delete views
2. **Notifications**: Notify students when exams are scheduled
3. **Exam analytics**: Show exam statistics and attendance
4. **Timetable import**: CSV import for bulk timetable creation
5. **Calendar integration**: Display exams on calendar widget
6. **Email notifications**: Send exam details to students

## Support

For issues or questions:
1. Check Django logs: `python manage.py runserver` output
2. Use Django admin to inspect model data
3. Review template context in views (add print statements for debugging)
4. Verify model relationships and foreign keys

## Summary of Changes

✓ Added 3 new views for exam scheduling and timetable management
✓ Added 2 new URL routes for exam features
✓ Created professional exam scheduling template with validation
✓ Enhanced timetable template with grid layout and image section
✓ Created static images directory structure
✓ No database migrations required (existing models used)

The implementation is ready for use after adding the timetable image and running the server!
