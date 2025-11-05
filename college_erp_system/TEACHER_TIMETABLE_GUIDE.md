# Teacher Timetable Setup Guide

## Overview
This guide explains how to create and manage personal timetables for teachers in the College ERP System.

## Fixed Issues

### ✅ Template Filter Error
**Error:** `Invalid filter: 'lookup'`

**Solution:** Created custom template tags in `academics/templatetags/timetable_filters.py`

The templates now properly load the custom filter:
```django
{% load timetable_filters %}
```

## Methods to Create Teacher Timetables

### Method 1: Using Management Command (Recommended for Bulk)

**Step 1:** Ensure the teacher account exists and has subjects assigned

**Step 2:** Run the population command:
```bash
python manage.py populate_teacher_timetable --teacher-username=<teacher_username>
```

**Example:**
```bash
python manage.py populate_teacher_timetable --teacher-username=bala.reddye
```

**What it does:**
- Clears existing timetable for the teacher (for 2025-2026)
- Creates all necessary time slots
- Populates timetable entries based on the schedule
- Provides detailed output of created entries

**Expected Output:**
```
Created time slot: monday 10:30:00-11:30:00
Added: Monday 10:30:00 - LEWT - VY 427 in VY 427
Added: Monday 14:30:00 - PP - VY 515 in VY 515
...
Successfully created 14 timetable entries for Balaganagadhar Reddy
```

### Method 2: Using Django Admin Interface

**Step 1:** Login to admin panel
```
http://localhost:8000/admin/
```

**Step 2:** Navigate to Academics → Teacher Timetables

**Step 3:** Click "Add Teacher Timetable"

**Step 4:** Fill in the form:
- **Teacher:** Select the teacher from dropdown
- **Subject:** Select subject (must be assigned to teacher)
- **Time Slot:** Select day and time
- **Room Number:** Enter room/venue code (e.g., VY 515)
- **Academic Year:** Will default to 2025-2026

**Step 5:** Click "Save" or "Save and add another"

**Tips:**
- You can filter by teacher, day, or academic year
- Use search to find specific teachers or subjects
- Bulk actions available for multiple entries

### Method 3: Creating Time Slots First

If time slots don't exist, create them first:

**Admin → Academics → Time Slots → Add Time Slot**

Example time slots:
- **Day:** Monday
- **Start Time:** 10:30
- **End Time:** 11:30

Then create Teacher Timetable entries using these slots.

## Teacher Timetable Data Structure

### Based on Provided Image for Bala Reddye

| Day | Time | Subject/Room | Duration |
|-----|------|--------------|----------|
| **Monday** | 10:30-11:30 | LEWT - VY 427 | 1 hour |
| **Monday** | 14:30-15:30 | PP - VY 515 | 1 hour |
| **Tuesday** | 10:30-11:30 | LEWT - VY 427 | 1 hour |
| **Tuesday** | 11:30-12:30 | PP - VY 325 | 1 hour |
| **Tuesday** | 14:30-15:30 | PP - VY 515 | 1 hour |
| **Tuesday** | 15:30-16:30 | RJS - VY 403 | 1 hour |
| **Wednesday** | 11:30-12:30 | PP - VY 515 | 1 hour |
| **Wednesday** | 12:30-13:30 | PP - VY 325 | 1 hour |
| **Wednesday** | 15:30-16:30 | RJS - VY 403 | 1 hour |
| **Thursday** | 11:30-12:30 | PP - VY 515 | 1 hour |
| **Thursday** | 12:30-13:30 | PP - VY 325 | 1 hour |
| **Thursday** | 15:30-16:30 | RJS - VY 403 | 1 hour |
| **Friday** | 11:30-12:30 | PP - VY 325 | 1 hour |
| **Friday** | 15:30-16:30 | RJS - VY 403 | 1 hour |

**Subject Codes:**
- **PP:** Python Programming
- **RJS:** React Js
- **LEWT:** Lab on Emerging Web Technology

## Prerequisites

### 1. Teacher Account Must Exist
- Teacher must be registered in the system
- `is_teacher` flag must be `True`
- Username must be known

### 2. Subjects Must Be Assigned
- Navigate to: Admin → Academics → Subjects
- Ensure subjects are created and assigned to the teacher
- At least one subject must be assigned

### 3. Class Must Be Assigned
- Subject must be linked to a class
- Class must have students enrolled

## Viewing Teacher Timetables

### As a Teacher:
1. Login with teacher credentials
2. Click "Timetable" in navigation menu
3. View personal weekly schedule

**Features:**
- Weekly grid view with color-coded cells
- Detailed schedule summary table
- Filter by academic year
- Hover effects on class cells
- Shows subject, class, room, and timing

### As an Admin:
1. Login to admin panel
2. Navigate to Academics → Teacher Timetables
3. View all timetable entries
4. Filter by teacher, day, or year
5. Edit or delete entries as needed

## Troubleshooting

### Issue 1: "No subjects found for teacher"

**Solution:**
1. Go to Admin → Academics → Subjects
2. Create or edit subjects
3. Assign the teacher to subjects
4. Run the command again

### Issue 2: "Teacher not found"

**Solution:**
1. Check username spelling
2. Verify teacher account exists: Admin → Accounts → Users
3. Ensure `is_teacher=True` is checked
4. Create teacher account if needed

### Issue 3: "Template error - Invalid filter: lookup"

**Solution:**
✅ **Already Fixed!** The custom template filter has been created.

If you still see this error:
1. Restart Django server
2. Clear browser cache
3. Check that `academics/templatetags/` folder exists
4. Verify `timetable_filters.py` is in templatetags folder

### Issue 4: Empty timetable page

**Solutions:**
1. Verify teacher has timetable entries:
   - Check admin → Teacher Timetables
   - Filter by teacher username

2. Check academic year filter matches
   - Default is 2025-2026
   - Entries must match selected year

3. Run population command:
   ```bash
   python manage.py populate_teacher_timetable --teacher-username=<username>
   ```

### Issue 5: Time slots not showing correctly

**Solution:**
1. Go to Admin → Academics → Time Slots
2. Verify time slots exist for the schedule
3. Create missing time slots manually
4. Ensure day names are lowercase (monday, tuesday, etc.)

## Adding Timetables for Multiple Teachers

### Option 1: Run Command for Each Teacher
```bash
python manage.py populate_teacher_timetable --teacher-username=teacher1
python manage.py populate_teacher_timetable --teacher-username=teacher2
python manage.py populate_teacher_timetable --teacher-username=teacher3
```

### Option 2: Use Admin Bulk Add
1. Open admin panel
2. Navigate to Teacher Timetables
3. Add entries one by one
4. Use "Save and add another" for efficiency

### Option 3: Customize Management Command
Edit `populate_teacher_timetable.py` to:
- Accept different schedule patterns
- Load from CSV/Excel
- Support multiple teachers in one run

## Student Timetable vs Teacher Timetable

### Student Timetable (Class-based)
- Shows all classes for a student's class/division
- Stored in: `Timetable` model
- Linked to: `Class` (e.g., FY MCA Div D)
- View: `students/timetable/`

### Teacher Timetable (Personal)
- Shows only classes taught by specific teacher
- Stored in: `TeacherTimetable` model
- Linked to: `Teacher` (specific user)
- View: `teachers/timetable/`

### Key Differences:
| Feature | Student Timetable | Teacher Timetable |
|---------|------------------|-------------------|
| Model | `Timetable` | `TeacherTimetable` |
| Scope | All students in class | Single teacher |
| Subject Filter | By class | By teacher |
| Use Case | Student schedule | Teacher schedule |

## Database Schema

### TeacherTimetable Model
```python
class TeacherTimetable(models.Model):
    teacher = ForeignKey(User)           # Teacher account
    subject = ForeignKey(Subject)        # Subject being taught
    time_slot = ForeignKey(TimeSlot)     # Day and time
    room_number = CharField              # Room/venue code
    academic_year = CharField            # e.g., "2025-2026"
```

### Relationships:
```
User (Teacher) ──┐
                 ├─→ TeacherTimetable ──→ TimeSlot (Day, Start, End)
Subject ─────────┘
```

## Best Practices

### 1. Consistent Naming
- Use standard room codes (VY 515, VY 403)
- Follow subject code conventions (PP, RJS, LEWT)
- Keep academic year format consistent (YYYY-YYYY)

### 2. Avoid Conflicts
- Check for scheduling conflicts before adding
- Ensure one teacher isn't scheduled in two places at same time
- Verify room availability

### 3. Regular Updates
- Update timetables each semester
- Archive old academic year data
- Review and verify before semester starts

### 4. Backup Data
- Export timetable data regularly
- Keep schedule spreadsheets as backup
- Document any changes

## Quick Reference Commands

```bash
# Check Django setup
python manage.py check

# Create time slots and timetable for a teacher
python manage.py populate_teacher_timetable --teacher-username=<username>

# Run server
python manage.py runserver

# Access admin
http://localhost:8000/admin/

# Access teacher timetable
http://localhost:8000/teachers/timetable/

# View migrations
python manage.py showmigrations

# Create superuser (if needed)
python manage.py createsuperuser
```

## Success Indicators

Your teacher timetable is set up correctly when:
- ✅ Teacher can login and view their personal timetable
- ✅ Weekly grid shows all scheduled classes
- ✅ Room numbers and timings are correct
- ✅ Subject details display properly
- ✅ No template errors occur
- ✅ Admin panel shows all entries
- ✅ Filters and search work correctly

## Next Steps

1. ✅ Test with one teacher first (e.g., Bala Reddye)
2. ✅ Verify display is correct
3. ✅ Add timetables for other teachers
4. ✅ Train teachers how to view their schedules
5. ✅ Set up conflict detection (optional enhancement)
6. ✅ Add print/export functionality (optional)

## Support

If you encounter issues not covered in this guide:
1. Check Django error logs
2. Review FEATURE_UPDATE_SUMMARY.md
3. Verify database migrations are applied
4. Ensure all prerequisites are met
5. Test with a simple example first

**Happy Scheduling! 📅**
