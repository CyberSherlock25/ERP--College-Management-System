# Quick Testing Guide for New Features

## Server Status
✅ Django development server is RUNNING on port 8000

## Features to Test

### 1. Academic Calendar (Students)

**URL to visit:**
```
http://localhost:8000/students/academic-calendar/
```

**What you should see:**
- Table showing all academic events for 2025-2026
- Events color-coded by type:
  - Green: Vacations (Diwali, Winter)
  - Yellow: Exams (Mid-term, Regular, Backlog)
  - Blue: Instructions
  - Primary: Term start
- Categorized view cards below the table
- Academic year dropdown filter

**Test Steps:**
1. Login as a student
2. Click "Academic Calendar" from dashboard or navigation
3. Verify all 9 events are displayed
4. Check date ranges are correct
5. Hover over events to see details

### 2. Student Dashboard - Calendar Widget

**URL to visit:**
```
http://localhost:8000/students/dashboard/
```

**What you should see:**
- New "Academic Calendar" widget on dashboard
- "Ongoing" events section (if any events are currently active)
- "Upcoming Events" list (next 5 events)
- "View All" button linking to full calendar
- "Quick Links" section with Academic Calendar link

**Test Steps:**
1. Login as a student
2. Check dashboard loads without errors
3. Verify calendar widget shows upcoming events
4. Click "View All" button
5. Test Quick Links navigation

### 3. Teacher Timetable

**URL to visit:**
```
http://localhost:8000/teachers/timetable/
```

**What you should see:**
- Weekly timetable grid
- Color-coded class cells (purple gradient)
- Time slots on left
- Days across the top
- Room numbers and class details
- Schedule summary table below

**Test Steps:**
1. Login as a teacher (Bala Reddye or another teacher)
2. Navigate to "Timetable"
3. Check weekly grid displays correctly
4. Verify schedule summary table
5. Hover over class cells to see animation
6. Test academic year filter dropdown

**Note:** Teacher must have:
- Subjects assigned in admin
- TeacherTimetable entries created

### 4. Admin Interface

**URL to visit:**
```
http://localhost:8000/admin/
```

**What to check:**
1. **Academic Calendars** section:
   - List view shows all events
   - Can add new events
   - Can edit existing events
   - Date hierarchy navigation works
   - Filters work (category, academic year)

2. **Teacher Timetables** section:
   - List view shows all timetable entries
   - Can add new entries
   - Can edit existing entries
   - Filters work (academic year, day, teacher)
   - Search works (teacher name, subject)

**Test Steps:**
1. Login as admin/superuser
2. Go to Academics section
3. Click "Academic Calendars"
4. Verify 9 entries exist for 2025-2026
5. Click "Teacher Timetables"
6. Check if entries exist (if teacher setup is complete)

## Data Population Commands

### Populate Academic Calendar
```bash
cd E:\MIT\Python\ERP--College-Management-System\college_erp_system
python manage.py populate_academic_calendar
```

**Expected Output:**
```
Successfully created 9 academic calendar events for 2025-2026
```

### Populate Teacher Timetable
```bash
# Replace 'bala.reddye' with actual teacher username
python manage.py populate_teacher_timetable --teacher-username=bala.reddye
```

**Expected Output:**
```
Successfully created X timetable entries for [Teacher Name]
```

**Prerequisites:**
- Teacher account must exist
- Teacher must be marked as `is_teacher=True`
- Teacher must have subjects assigned

## Troubleshooting

### Issue: Server not running
**Solution:**
```powershell
cd E:\MIT\Python\ERP--College-Management-System\college_erp_system
python manage.py runserver
```

### Issue: No calendar events showing
**Solution:**
```bash
python manage.py populate_academic_calendar
```

### Issue: Teacher timetable is empty
**Solutions:**
1. Check if teacher has subjects assigned:
   - Go to admin → Academics → Subjects
   - Assign subjects to the teacher

2. Run timetable population command:
```bash
python manage.py populate_teacher_timetable --teacher-username=<teacher_username>
```

3. Manually add entries in admin:
   - Go to admin → Academics → Teacher Timetables
   - Click "Add Teacher Timetable"

### Issue: Template errors or 404
**Solutions:**
1. Check URLs are correct
2. Clear browser cache
3. Restart Django server
4. Check if user is logged in
5. Verify user has correct permissions (is_student/is_teacher)

## Quick Verification Checklist

- [ ] Server is running (http://localhost:8000)
- [ ] Can login as student
- [ ] Can login as teacher
- [ ] Can login as admin
- [ ] Academic calendar shows 9 events for 2025-2026
- [ ] Student dashboard shows calendar widget
- [ ] Teacher timetable page loads
- [ ] Admin interface shows new models
- [ ] All migrations are applied
- [ ] No console errors in browser

## Sample Test Accounts

You'll need to create or use existing accounts:

### Student Account
- Username: [Your student username]
- Must have `is_student=True`
- Must be assigned to a class

### Teacher Account  
- Username: [Your teacher username, e.g., bala.reddye]
- Must have `is_teacher=True`
- Must have subjects assigned

### Admin Account
- Username: [Your admin username]
- Must have `is_superuser=True`

## Browser Console Check

Open browser developer tools (F12) and check:
1. No JavaScript errors in Console tab
2. No 404 errors in Network tab
3. CSS loads correctly
4. All images/icons load

## Expected Data

### Academic Calendar Events (2025-2026)
1. Commencement of Term - Jul 7, 2025
2. Induction - Jul 7-8, 2025  
3. Academic Instruction Duration - Jul 8 - Nov 18
4. Mid Term Exam - Sep 29 - Oct 10, 2025
5. Diwali Vacation - Oct 18-25, 2025
6. Last Instructional Day - Dec 12, 2025
7. Term End Exam (Backlog) - Nov 19-30, 2025
8. Term End Exam (Regular) - Dec 1-22, 2025
9. Winter Vacation - Dec 23, 2025 - Jan 4, 2026

### Teacher Timetable (Sample for Bala Reddye)
Based on provided image:
- Monday: 3 classes
- Tuesday: 3 classes  
- Wednesday: 2 classes
- Thursday: 2 classes
- Friday: 2 classes

## Next Steps After Testing

1. ✅ Verify all features work
2. ✅ Populate real data for all teachers
3. ✅ Add more academic years if needed
4. ✅ Customize colors/styles if desired
5. ✅ Train users on new features
6. ✅ Monitor for any bugs or issues

## Support

If you encounter issues:
1. Check this guide first
2. Review FEATURE_UPDATE_SUMMARY.md
3. Check Django error logs
4. Verify database migrations
5. Ensure all prerequisites are met

## Success Indicators

Your implementation is successful when:
- ✅ All pages load without errors
- ✅ Calendar shows correct events
- ✅ Teacher timetable displays properly
- ✅ Student dashboard includes calendar widget
- ✅ Admin interface works correctly
- ✅ No migration warnings
- ✅ No console errors

**Happy Testing! 🎉**
