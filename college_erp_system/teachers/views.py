from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from collections import defaultdict

from academics.models import Class, Subject, Attendance, Course, Timetable, Exam, TimeSlot, TeacherTimetable
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
    """Display organized teacher timetable in grid format."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')

    # Get selected academic year from GET params
    selected_year = request.GET.get('year', '2025-2026')
    
    # Get teacher's timetable
    teacher_timetable_objs = TeacherTimetable.objects.filter(
        teacher=request.user,
        academic_year=selected_year
    ).select_related('subject__course', 'subject__class_assigned', 'time_slot').order_by(
        'time_slot__day', 'time_slot__start_time'
    )
    
    # Organize timetable by day for grid display
    organized_timetable = defaultdict(list)
    time_slots_set = set()
    days_set = set()
    
    for entry in teacher_timetable_objs:
        day = entry.time_slot.day.lower()
        organized_timetable[day].append(entry)
        days_set.add(day)
        time_slots_set.add((entry.time_slot.start_time, entry.time_slot.end_time))
    
    # Convert to sorted lists
    days = sorted(list(days_set), key=lambda x: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].index(x))
    time_slots = sorted(list(time_slots_set))
    
    # Get available academic years
    academic_years = TeacherTimetable.objects.filter(
        teacher=request.user
    ).values_list('academic_year', flat=True).distinct().order_by('-academic_year')
    
    context = {
        'teacher_timetable': teacher_timetable_objs,
        'organized_timetable': organized_timetable,
        'days': days,
        'time_slots': time_slots,
        'academic_years': academic_years or ['2025-2026'],
        'selected_year': selected_year,
    }
    return render(request, 'teachers/timetable.html', context)


@login_required
def exam_select(request):
    """Allow a teacher to select subjects and schedule an exam."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    # Get subjects taught by this teacher
    subjects = Subject.objects.filter(
        teacher=request.user
    ).select_related('course', 'class_assigned').order_by('course__code')
    
    # Get time slots for the form
    time_slots = TimeSlot.objects.all().order_by('start_time')
    
    context = {
        'subjects': subjects,
        'time_slots': time_slots,
        'exam_types': Exam.EXAM_TYPE_CHOICES,
    }
    return render(request, 'teachers/exam_select.html', context)


@login_required
def schedule_exam(request):
    """Create exam records for selected subjects."""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        exam_name = request.POST.get('exam_name', '').strip()
        exam_type = request.POST.get('exam_type', 'quiz')
        exam_date = request.POST.get('exam_date')
        exam_time = request.POST.get('exam_time')
        duration_hours = request.POST.get('duration_hours', '1')
        duration_minutes = request.POST.get('duration_minutes', '0')
        total_marks = request.POST.get('total_marks', '100')
        pass_marks = request.POST.get('pass_marks', '40')
        instructions = request.POST.get('instructions', '').strip()
        selected_subjects = request.POST.getlist('subjects')
        
        # Validation
        if not exam_name:
            messages.error(request, "Exam name is required.")
            return redirect('teachers:exam_select')
        
        if not selected_subjects:
            messages.error(request, "Please select at least one subject.")
            return redirect('teachers:exam_select')
        
        try:
            total_marks = int(total_marks)
            pass_marks = int(pass_marks)
            duration_hours = int(duration_hours)
            duration_minutes = int(duration_minutes)
            
            if total_marks < 1 or pass_marks < 1:
                raise ValueError("Marks must be positive numbers.")
            if pass_marks > total_marks:
                raise ValueError("Pass marks cannot exceed total marks.")
        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid input: {str(e)}")
            return redirect('teachers:exam_select')
        
        # Combine date and time
        try:
            exam_datetime = datetime.fromisoformat(f"{exam_date}T{exam_time}")
        except (ValueError, TypeError):
            messages.error(request, "Invalid date or time format.")
            return redirect('teachers:exam_select')
        
        # Calculate duration
        duration = timedelta(hours=duration_hours, minutes=duration_minutes)
        
        # Create exam for each selected subject
        created_count = 0
        for subject_id in selected_subjects:
            try:
                subject = Subject.objects.get(
                    id=subject_id,
                    teacher=request.user
                )
                exam = Exam.objects.create(
                    name=exam_name,
                    exam_type=exam_type,
                    subject=subject,
                    date=exam_datetime,
                    duration=duration,
                    total_marks=total_marks,
                    pass_marks=pass_marks,
                    instructions=instructions,
                    created_by=request.user
                )
                created_count += 1
            except Subject.DoesNotExist:
                messages.warning(request, f"Subject ID {subject_id} not found or not assigned to you.")
                continue
        
        if created_count > 0:
            messages.success(request, f"Successfully created {created_count} exam record(s) for {exam_name}.")
            return redirect('teachers:dashboard')
        else:
            messages.error(request, "No exams were created. Please check the selected subjects.")
            return redirect('teachers:exam_select')
    
    return redirect('teachers:exam_select')


@login_required
def my_classes(request):
    """Display classes managed by the teacher"""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    from students.models import Student
    
    managed_classes = Class.objects.filter(
        class_teacher=request.user
    ).select_related('department')
    
    classes_data = []
    for cls in managed_classes:
        students = Student.objects.filter(student_class=cls).select_related('user').count()
        subjects = Subject.objects.filter(class_assigned=cls).count()
        classes_data.append({
            'class': cls,
            'students_count': students,
            'subjects_count': subjects,
        })
    
    context = {
        'classes_data': classes_data,
    }
    return render(request, 'teachers/my_classes.html', context)


@login_required
def enter_grades(request):
    """Allow teachers to enter student grades for exams"""
    if not request.user.is_teacher:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    from academics.models import Result
    from students.models import Student
    
    selected_exam_id = request.GET.get('exam')
    selected_exam = None
    students_results = []
    
    # Get exams created by this teacher
    my_exams = Exam.objects.filter(
        created_by=request.user
    ).select_related('subject__course', 'subject__class_assigned')
    
    if selected_exam_id:
        try:
            selected_exam = my_exams.get(id=selected_exam_id)
            # Get all students in the class
            students = Student.objects.filter(
                student_class=selected_exam.subject.class_assigned
            ).select_related('user')
            
            for student in students:
                result, created = Result.objects.get_or_create(
                    student=student.user,
                    exam=selected_exam
                )
                students_results.append({
                    'student': student,
                    'result': result,
                })
        except Exam.DoesNotExist:
            messages.error(request, "Exam not found.")
    
    if request.method == 'POST':
        marks_data = {}
        remarks_data = {}
        
        for key, value in request.POST.items():
            if key.startswith('marks_'):
                result_id = key.split('marks_')[1]
                marks_data[result_id] = value
            elif key.startswith('remarks_'):
                result_id = key.split('remarks_')[1]
                remarks_data[result_id] = value
        
        updated_count = 0
        for result_id, marks in marks_data.items():
            try:
                marks = int(marks)
                if marks < 0 or marks > selected_exam.total_marks:
                    messages.warning(request, f"Invalid marks: {marks}. Must be 0-{selected_exam.total_marks}")
                    continue
                
                result = Result.objects.get(id=result_id)
                result.marks_obtained = marks
                result.remarks = remarks_data.get(result_id, '')
                result.save()
                updated_count += 1
            except (ValueError, Result.DoesNotExist):
                continue
        
        messages.success(request, f"Updated grades for {updated_count} students.")
        return redirect(f'teachers:enter_grades?exam={selected_exam_id}')
    
    context = {
        'my_exams': my_exams,
        'selected_exam': selected_exam,
        'students_results': students_results,
    }
    return render(request, 'teachers/enter_grades.html', context)
