from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from academics.models import Class, Subject, Attendance, Course, Timetable, Exam, TeacherTimetable, AcademicCalendar
from students.models import Student, Notification


def create_attendance_notification(subject, date, marked_by, students):
    """Create attendance notifications for students when attendance is marked"""
    # Create notification for the class
    notification = Notification.objects.create(
        title=f"Attendance Marked - {subject.course.name}",
        message=f"Attendance has been marked for {subject.course.name} on {date.strftime('%B %d, %Y')} by {marked_by.get_full_name()}.",
        notification_type='academic',
        target_audience='class',
        target_class=subject.class_assigned,
        created_by=marked_by,
        is_urgent=False
    )
    
    # Also create individual notifications for each student
    for student in students:
        Notification.objects.create(
            title=f"Your Attendance Marked - {subject.course.name}",
            message=f"Your attendance for {subject.course.name} on {date.strftime('%B %d, %Y')} has been marked by {marked_by.get_full_name()}. Check your attendance records for details.",
            notification_type='academic',
            target_audience='individual_student',
            target_student=student,
            created_by=marked_by,
            is_urgent=False
        )


@login_required
def dashboard(request):
    """Teacher dashboard with overview similar to student/admin dashboards."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')

    teacher_user = request.user

    # Subjects taught by this teacher
    subjects = Subject.objects.filter(teacher=teacher_user).select_related('course', 'class_assigned')

    # Classes managed by this teacher as class teacher
    managed_classes = Class.objects.filter(class_teacher=teacher_user).select_related('department')

    # Today's timetable slots for teacher's subjects
    today = timezone.now().date()
    weekday = today.strftime('%A').lower()
    todays_slots = Timetable.objects.filter(
        subject__in=subjects,
        time_slot__day=weekday,
    ).select_related('subject__course', 'class_assigned', 'time_slot').order_by('time_slot__start_time')

    # Upcoming exams for teacher's subjects
    upcoming_exams = Exam.objects.filter(
        subject__in=subjects,
        date__gte=timezone.now()
    ).select_related('subject__course').order_by('date')[:5]

    # Recent attendance marked by this teacher
    recent_marked_attendance = Attendance.objects.filter(
        marked_by=teacher_user
    ).select_related('subject__course', 'student').order_by('-date')[:10]

    # Pending attendance to mark today (subjects where no records exist for today)
    pending_today = []
    for sub in subjects:
        has_today = Attendance.objects.filter(subject=sub, date=today).exists()
        if not has_today:
            pending_today.append(sub)

    # Notifications targeting teachers
    teacher_notifications = Notification.objects.filter(
        # all + all_teachers + department + individual_teacher
        target_audience__in=['all', 'all_teachers']
    ).order_by('-created_at')[:5]

    context = {
        'subjects': subjects,
        'managed_classes': managed_classes,
        'todays_slots': todays_slots,
        'upcoming_exams': upcoming_exams,
        'recent_marked_attendance': recent_marked_attendance,
        'pending_today': pending_today,
        'today': today,
    }
    return render(request, 'teachers/dashboard.html', context)

@login_required
def attendance_select(request):
    """Allow a teacher to select semester, subject, and date to mark attendance."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')

    # Get filter parameters
    selected_semester = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')
    selected_date = request.GET.get('date') or timezone.now().date().isoformat()

    # Get all semesters that have subjects
    semesters = Course.SEMESTER_CHOICES
    
    # Filter subjects assigned to the logged-in teacher
    subjects = Subject.objects.filter(teacher=request.user).select_related(
        'course', 'course__department', 'class_assigned'
    ).order_by('course__semester', 'course__department__code', 'course__code')
    
    # Filter by selected semester if provided
    if selected_semester:
        subjects = subjects.filter(course__semester=int(selected_semester))

    selected_subject = None
    students = []
    if selected_subject_id:
        selected_subject = get_object_or_404(subjects, id=selected_subject_id)
        # Students in the class for this subject, ordered by roll number
        students = Student.objects.filter(
            student_class=selected_subject.class_assigned
        ).select_related('user').order_by('roll_number')

    context = {
        'semesters': semesters,
        'selected_semester': selected_semester,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'students': students,
        'selected_date': selected_date,
    }
    return render(request, 'teachers/attendance_select.html', context)


@login_required
@transaction.atomic
def attendance_mark(request, subject_id):
    """Mark attendance for all students in a class for a subject and date."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')

    # Only allow teacher assigned to this subject to mark attendance
    subject = get_object_or_404(
        Subject.objects.select_related('course', 'class_assigned'), 
        id=subject_id,
        teacher=request.user
    )
    date_str = request.POST.get('date') if request.method == 'POST' else request.GET.get('date')
    try:
        date = timezone.datetime.fromisoformat(date_str).date() if date_str else timezone.now().date()
    except ValueError:
        date = timezone.now().date()

    # Pull students of the class
    students = Student.objects.filter(student_class=subject.class_assigned).select_related('user').order_by('roll_number')

    if request.method == 'POST':
        present_ids = set(request.POST.getlist('present'))
        remarks_map = {}
        for key, value in request.POST.items():
            if key.startswith('remark_'):
                student_id = key.split('remark_')[1]
                remarks_map[student_id] = value

        created, updated = 0, 0
        for student in students:
            is_present = str(student.id) in present_ids
            remarks = remarks_map.get(str(student.id), '')

            obj, existed = Attendance.objects.update_or_create(
                student=student.user,
                subject=subject,
                date=date,
                defaults={
                    'is_present': is_present,
                    'remarks': remarks,
                    'marked_by': request.user,
                }
            )
            if existed:
                updated += 1
            else:
                created += 1

        # Create notifications for students
        create_attendance_notification(subject, date, request.user, students)
        
        messages.success(request, f"Attendance saved for {subject.course.name} on {date}. Created {created}, updated {updated}.")
        return redirect('teachers:attendance')

    # For GET, preload existing marks if any
    existing = Attendance.objects.filter(subject=subject, date=date).select_related('student')
    existing_map = {rec.student_id: rec for rec in existing}

    rows = []
    for st in students:
        rec = existing_map.get(st.user.id)
        rows.append({
            'student': st,
            'is_present': rec.is_present if rec else False,
            'remarks': rec.remarks if rec else '',
        })

    context = {
        'subject': subject,
        'students': students,
        'date': date,
        'rows': rows,
    }
    return render(request, 'teachers/attendance_mark.html', context)

@login_required
def teacher_timetable(request):
    """Display teacher's personal timetable"""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    teacher_user = request.user
    
    # Get filter parameters
    selected_year = request.GET.get('year', '2025-2026')
    
    # Get teacher's timetable
    teacher_timetable = TeacherTimetable.objects.filter(
        teacher=teacher_user,
        academic_year=selected_year
    ).select_related('subject__course', 'subject__class_assigned', 'time_slot').order_by(
        'time_slot__day', 'time_slot__start_time'
    )
    
    # Organize timetable by day
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    organized_timetable = {}
    
    for day in days:
        organized_timetable[day] = teacher_timetable.filter(time_slot__day=day)
    
    # Get all unique time slots
    time_slots = teacher_timetable.values_list(
        'time_slot__start_time', 'time_slot__end_time'
    ).distinct().order_by('time_slot__start_time')
    
    # Get unique academic years
    academic_years = TeacherTimetable.objects.values_list('academic_year', flat=True).distinct()
    
    context = {
        'teacher_timetable': teacher_timetable,
        'organized_timetable': organized_timetable,
        'days': days,
        'time_slots': time_slots,
        'academic_years': academic_years,
        'selected_year': selected_year,
    }
    return render(request, 'teachers/timetable.html', context)
