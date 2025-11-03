from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from students.models import Student, Notification
from teachers.models import Teacher
from academics.models import (
    Department, Course, Class, Subject, Attendance, 
    Exam, Result, Fee, Timetable
)


def is_admin_user(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.is_admin)


@login_required
@user_passes_test(is_admin_user)
def dashboard(request):
    """Administration dashboard with comprehensive statistics"""
    context = {}
    
    # Basic Statistics
    context['total_students'] = Student.objects.filter(is_active=True).count()
    context['total_teachers'] = Teacher.objects.filter(is_active=True).count()
    context['total_departments'] = Department.objects.count()
    context['total_courses'] = Course.objects.count()
    context['total_classes'] = Class.objects.count()
    
    # Attendance Analytics
    one_week_ago = timezone.now().date() - timedelta(days=7)
    weekly_attendance = Attendance.objects.filter(
        date__gte=one_week_ago,
        date__lte=timezone.now().date()
    ).aggregate(
        avg_attendance=Avg('is_present')
    )
    
    attendance_percentage = 0
    if weekly_attendance['avg_attendance']:
        attendance_percentage = round(weekly_attendance['avg_attendance'] * 100, 1)
    context['attendance_percentage'] = attendance_percentage
    
    # Upcoming Exams (Next 7 days)
    next_week = timezone.now() + timedelta(days=7)
    context['upcoming_exams'] = Exam.objects.filter(
        date__gte=timezone.now(),
        date__lte=next_week
    ).count()
    
    # Pending Fees Statistics
    pending_fees = Fee.objects.filter(
        payment_status__in=['pending', 'partial', 'overdue']
    ).aggregate(
        count=Count('id'),
        total_amount=Sum('amount')
    )
    
    context['pending_fees_count'] = pending_fees['count'] or 0
    context['pending_fees_amount'] = pending_fees['total_amount'] or Decimal('0.00')
    
    # Recent Notifications (Last 7 days)
    context['recent_notifications'] = Notification.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5]
    
    # Department Statistics
    department_stats = []
    total_students_count = context['total_students']
    
    for dept in Department.objects.all():
        dept_student_count = Student.objects.filter(
            department=dept,
            is_active=True
        ).count()
        
        percentage = 0
        if total_students_count > 0:
            percentage = round((dept_student_count / total_students_count) * 100, 1)
        
        department_stats.append({
            'dept': dept,
            'student_count': dept_student_count,
            'percentage': percentage
        })
    
    context['department_stats'] = department_stats
    
    # Add data for notice modal
    context['all_students'] = Student.objects.filter(is_active=True).select_related('user', 'department').order_by('user__first_name')
    context['all_teachers'] = Teacher.objects.filter(is_active=True).select_related('user', 'department').order_by('user__first_name')
    
    return render(request, 'administration/dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def get_dashboard_analytics(request):
    """API endpoint for dashboard analytics data"""
    
    # Monthly student enrollment data
    monthly_data = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(month=month_start.month % 12 + 1, day=1) - timedelta(days=1)
        
        student_count = Student.objects.filter(
            admission_date__gte=month_start,
            admission_date__lte=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'students': student_count
        })
    
    # Department wise performance
    dept_performance = []
    for dept in Department.objects.all():
        # Calculate average marks for the department
        avg_marks = Result.objects.filter(
            student__student_profile__department=dept,
            is_published=True
        ).aggregate(avg_marks=Avg('marks_obtained'))
        
        dept_performance.append({
            'department': dept.name,
            'avg_performance': avg_marks['avg_marks'] or 0
        })
    
    # Fee collection status
    fee_status = Fee.objects.values('payment_status').annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    return JsonResponse({
        'monthly_enrollment': monthly_data,
        'department_performance': dept_performance,
        'fee_status': list(fee_status)
    })


@login_required
@user_passes_test(is_admin_user)
def send_notification(request):
    """Send broadcast notifications"""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        message = request.POST.get('message', '')
        notification_type = request.POST.get('notification_type', 'general')
        target_audience = request.POST.get('target_audience', 'all')
        is_urgent = request.POST.get('is_urgent') == 'on'
        
        # Create notification
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            target_audience=target_audience,
            is_urgent=is_urgent,
            created_by=request.user
        )
        
        # Handle specific targeting
        if target_audience == 'class':
            class_id = request.POST.get('target_class')
            if class_id:
                notification.target_class_id = class_id
                notification.save()
        
        elif target_audience == 'department':
            dept_id = request.POST.get('target_department')
            if dept_id:
                notification.target_department_id = dept_id
                notification.save()
        
        elif target_audience == 'individual':
            student_id = request.POST.get('target_student')
            if student_id:
                notification.target_student_id = student_id
                notification.save()
        
        return redirect('administration:dashboard')
    
    # GET request - show form
    context = {
        'departments': Department.objects.all(),
        'classes': Class.objects.all(),
        'students': Student.objects.filter(is_active=True).select_related('user'),
    }
    return render(request, 'administration/send_notification.html', context)


@login_required
@user_passes_test(is_admin_user)
def send_notice(request):
    """Send notice to students/teachers (individual or bulk)"""
    if request.method == 'POST':
        try:
            from accounts.models import User
            
            title = request.POST.get('title', '').strip()
            message = request.POST.get('message', '').strip()
            notice_type = request.POST.get('notice_type', 'general')
            recipient_type = request.POST.get('recipient_type', '')
            is_urgent = 'is_urgent' in request.POST
            send_email = 'send_email' in request.POST
            
            if not title or not message:
                messages.error(request, '❌ Title and message are required!')
                return redirect('administration:dashboard')
            
            notifications_created = 0
            recipient_description = ""
            
            # Determine recipients based on type and create notifications
            if recipient_type == 'all':
                # All students
                students = Student.objects.filter(is_active=True)
                for student in students:
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='all_students',
                        target_student=student,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                
                # All teachers
                teachers = Teacher.objects.filter(is_active=True)
                for teacher in teachers:
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='all_teachers',
                        target_teacher=teacher,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                    
                recipient_description = "Everyone (Students & Teachers)"
                
            elif recipient_type == 'all_students':
                # All students
                students = Student.objects.filter(is_active=True)
                for student in students:
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='all_students',
                        target_student=student,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                    
                recipient_description = "All Students"
                
            elif recipient_type == 'all_teachers':
                # All teachers
                teachers = Teacher.objects.filter(is_active=True)
                for teacher in teachers:
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='all_teachers',
                        target_teacher=teacher,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                    
                recipient_description = "All Teachers"
                
            elif recipient_type == 'department':
                # Specific department
                dept_id = request.POST.get('department_id')
                if dept_id:
                    dept = Department.objects.get(id=dept_id)
                    
                    # Students in this department
                    students = Student.objects.filter(department=dept, is_active=True)
                    for student in students:
                        Notification.objects.create(
                            title=title,
                            message=message,
                            notification_type=notice_type,
                            target_audience='department',
                            target_department=dept,
                            target_student=student,
                            is_urgent=is_urgent,
                            send_email=send_email,
                            created_by=request.user
                        )
                        notifications_created += 1
                    
                    # Teachers in this department
                    teachers = Teacher.objects.filter(department=dept, is_active=True)
                    for teacher in teachers:
                        Notification.objects.create(
                            title=title,
                            message=message,
                            notification_type=notice_type,
                            target_audience='department',
                            target_department=dept,
                            target_teacher=teacher,
                            is_urgent=is_urgent,
                            send_email=send_email,
                            created_by=request.user
                        )
                        notifications_created += 1
                        
                    recipient_description = f"Department: {dept.name}"
                    
            elif recipient_type == 'specific_student':
                # Specific student
                student_id = request.POST.get('student_id')
                if student_id:
                    student = Student.objects.get(id=student_id)
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='individual_student',
                        target_student=student,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                    recipient_description = f"Student: {student.user.get_full_name()} ({student.roll_number})"
                    
            elif recipient_type == 'specific_teacher':
                # Specific teacher
                teacher_id = request.POST.get('teacher_id')
                if teacher_id:
                    teacher = Teacher.objects.get(id=teacher_id)
                    Notification.objects.create(
                        title=title,
                        message=message,
                        notification_type=notice_type,
                        target_audience='individual_teacher',
                        target_teacher=teacher,
                        is_urgent=is_urgent,
                        send_email=send_email,
                        created_by=request.user
                    )
                    notifications_created += 1
                    recipient_description = f"Teacher: {teacher.user.get_full_name()} ({teacher.employee_id})"
            
            if notifications_created == 0:
                messages.error(request, '❌ No recipients selected!')
                return redirect('administration:dashboard')
            
            # Success message
            urgency_text = "🚨 Urgent " if is_urgent else ""
            messages.success(
                request, 
                f'✅ {urgency_text}Notice sent successfully to {notifications_created} recipient(s)! '
                f'Target: {recipient_description}'
            )
            
        except Exception as e:
            messages.error(request, f'❌ Error sending notice: {str(e)}')
    
    return redirect('administration:dashboard')


@login_required
@user_passes_test(is_admin_user)
def system_reports(request):
    """Generate various system reports"""
    report_type = request.GET.get('type', 'overview')
    
    context = {
        'report_type': report_type,
        'generated_at': timezone.now()
    }
    
    if report_type == 'attendance':
        # Attendance report
        date_from = request.GET.get('from_date')
        date_to = request.GET.get('to_date')
        
        if date_from and date_to:
            attendance_data = Attendance.objects.filter(
                date__range=[date_from, date_to]
            ).select_related('student', 'subject__course', 'subject__class_assigned')
            
            context['attendance_records'] = attendance_data
            context['date_range'] = f"{date_from} to {date_to}"
    
    elif report_type == 'financial':
        # Financial report
        current_year = timezone.now().year
        financial_data = Fee.objects.filter(
            academic_year__contains=str(current_year)
        ).values('payment_status').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        context['financial_summary'] = financial_data
        context['total_revenue'] = Fee.objects.filter(
            payment_status='paid',
            academic_year__contains=str(current_year)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    elif report_type == 'academic':
        # Academic performance report
        academic_data = []
        for dept in Department.objects.all():
            dept_results = Result.objects.filter(
                student__student_profile__department=dept,
                is_published=True
            ).aggregate(
                avg_marks=Avg('marks_obtained'),
                pass_rate=Avg('marks_obtained__gte', 
                            filter=Q(exam__pass_marks__lte=F('marks_obtained')))
            )
            
            academic_data.append({
                'department': dept,
                'avg_marks': dept_results['avg_marks'] or 0,
                'pass_rate': dept_results['pass_rate'] or 0
            })
        
        context['academic_performance'] = academic_data
    
    return render(request, 'administration/reports.html', context)


@login_required
@user_passes_test(is_admin_user)
def manage_users(request):
    """Manage students and teachers with advanced filtering"""
    user_type = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', 'active')
    sort_by = request.GET.get('sort', 'name')
    
    context = {
        'user_type': user_type,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'departments': Department.objects.all().order_by('name')
    }
    
    # ALL USERS VIEW
    if user_type == 'all':
        from accounts.models import User
        users = User.objects.all().select_related('student_profile', 'teacher_profile')
        
        # Apply filters
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        
        # Sort
        if sort_by == 'name':
            users = users.order_by('first_name', 'last_name')
        elif sort_by == 'date':
            users = users.order_by('-date_joined')
        elif sort_by == 'type':
            users = users.order_by('user_type')
        
        context['all_users'] = users
        context['total_users'] = users.count()
        context['admin_count'] = users.filter(user_type='admin').count()
        context['teacher_count'] = users.filter(user_type='teacher').count()
        context['student_count'] = users.filter(user_type='student').count()
    
    # STUDENTS VIEW
    elif user_type == 'students':
        students = Student.objects.all().select_related('user', 'department', 'student_class')
        
        # Apply filters
        if search_query:
            students = students.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(roll_number__icontains=search_query) |
                Q(admission_number__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        if department_filter:
            students = students.filter(department_id=department_filter)
        
        if status_filter == 'active':
            students = students.filter(is_active=True)
        elif status_filter == 'inactive':
            students = students.filter(is_active=False)
        
        # Sort
        if sort_by == 'name':
            students = students.order_by('user__first_name', 'user__last_name')
        elif sort_by == 'roll':
            students = students.order_by('roll_number')
        elif sort_by == 'date':
            students = students.order_by('-admission_date')
        elif sort_by == 'department':
            students = students.order_by('department__name')
        
        context['students'] = students
        context['total_students'] = students.count()
    
    # TEACHERS VIEW
    elif user_type == 'teachers':
        teachers = Teacher.objects.all().select_related('user', 'department')
        
        # Apply filters
        if search_query:
            teachers = teachers.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(designation__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(specialization__icontains=search_query)
            )
        
        if department_filter:
            teachers = teachers.filter(department_id=department_filter)
        
        if status_filter == 'active':
            teachers = teachers.filter(is_active=True)
        elif status_filter == 'inactive':
            teachers = teachers.filter(is_active=False)
        
        # Sort
        if sort_by == 'name':
            teachers = teachers.order_by('user__first_name', 'user__last_name')
        elif sort_by == 'employee':
            teachers = teachers.order_by('employee_id')
        elif sort_by == 'date':
            teachers = teachers.order_by('-joining_date')
        elif sort_by == 'department':
            teachers = teachers.order_by('department__name')
        elif sort_by == 'designation':
            teachers = teachers.order_by('designation')
        
        context['teachers'] = teachers
        context['total_teachers'] = teachers.count()
    
    return render(request, 'administration/manage_users.html', context)


@login_required
@user_passes_test(is_admin_user)
def department_details(request, dept_id):
    """Detailed view of a specific department"""
    
    department = get_object_or_404(Department, id=dept_id)
    
    # Department statistics
    dept_students = Student.objects.filter(department=department, is_active=True)
    dept_teachers = Teacher.objects.filter(department=department, is_active=True)
    dept_courses = Course.objects.filter(department=department)
    dept_classes = Class.objects.filter(department=department)
    
    # Performance metrics
    performance_data = Result.objects.filter(
        student__student_profile__department=department,
        is_published=True
    ).aggregate(
        avg_marks=Avg('marks_obtained'),
        total_exams=Count('exam', distinct=True),
        total_results=Count('id')
    )
    
    # Recent notifications for this department
    dept_notifications = Notification.objects.filter(
        Q(target_department=department) | Q(target_audience='all')
    ).order_by('-created_at')[:10]
    
    context = {
        'department': department,
        'students': dept_students,
        'teachers': dept_teachers,
        'courses': dept_courses,
        'classes': dept_classes,
        'student_count': dept_students.count(),
        'teacher_count': dept_teachers.count(),
        'course_count': dept_courses.count(),
        'class_count': dept_classes.count(),
        'performance': performance_data,
        'notifications': dept_notifications
    }
    
    return render(request, 'administration/department_details.html', context)


@login_required
@user_passes_test(is_admin_user)
def quick_actions(request):
    """Handle quick administrative actions"""
    action = request.POST.get('action')
    
    if action == 'bulk_notification':
        # Handle bulk notification sending
        target_ids = request.POST.getlist('target_ids[]')
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        # Create notifications for selected users
        for target_id in target_ids:
            Notification.objects.create(
                title=title,
                message=message,
                target_audience='individual',
                target_student_id=target_id,
                created_by=request.user
            )
    
    elif action == 'generate_report':
        # Generate and download reports
        report_type = request.POST.get('report_type')
        # Implementation for report generation
        pass
    
    elif action == 'backup_data':
        # Trigger data backup
        # Implementation for data backup
        pass
    
    return redirect('administration:dashboard')


@login_required
@user_passes_test(is_admin_user)
def export_data(request):
    """Export various data to CSV/Excel formats"""
    
    export_type = request.GET.get('type', 'students')
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        if export_type == 'students':
            writer.writerow(['Roll Number', 'Name', 'Department', 'Class', 'Admission Date', 'Status'])
            
            students = Student.objects.filter(is_active=True).select_related(
                'user', 'department', 'student_class'
            )
            
            for student in students:
                writer.writerow([
                    student.roll_number,
                    student.user.get_full_name(),
                    student.department.name,
                    student.student_class.name if student.student_class else 'N/A',
                    student.admission_date,
                    'Active' if student.is_active else 'Inactive'
                ])
        
        elif export_type == 'teachers':
            writer.writerow(['Employee ID', 'Name', 'Department', 'Designation', 'Joining Date', 'Status'])
            
            teachers = Teacher.objects.filter(is_active=True).select_related(
                'user', 'department'
            )
            
            for teacher in teachers:
                writer.writerow([
                    teacher.employee_id,
                    teacher.user.get_full_name(),
                    teacher.department.name,
                    teacher.designation,
                    teacher.joining_date,
                    'Active' if teacher.is_active else 'Inactive'
                ])
        
        elif export_type == 'fees':
            writer.writerow(['Student', 'Fee Type', 'Amount', 'Due Date', 'Status', 'Academic Year'])
            
            fees = Fee.objects.all().select_related('student')
            
            for fee in fees:
                writer.writerow([
                    fee.student.get_full_name(),
                    fee.get_fee_type_display(),
                    fee.amount,
                    fee.due_date,
                    fee.get_payment_status_display(),
                    fee.academic_year
                ])
        
        return response
    
    return redirect('administration:dashboard')


@login_required
@user_passes_test(is_admin_user)
def attendance_overview(request):
    """Comprehensive attendance overview"""
    date_from = request.GET.get('from_date', (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('to_date', timezone.now().strftime('%Y-%m-%d'))
    department_id = request.GET.get('department')
    
    # Filter criteria
    filters = {
        'date__range': [date_from, date_to]
    }
    
    if department_id:
        filters['subject__class_assigned__department_id'] = department_id
    
    # Attendance statistics
    attendance_records = Attendance.objects.filter(**filters)
    
    total_records = attendance_records.count()
    present_records = attendance_records.filter(is_present=True).count()
    
    overall_percentage = 0
    if total_records > 0:
        overall_percentage = round((present_records / total_records) * 100, 2)
    
    # Class-wise attendance
    class_attendance = attendance_records.values(
        'subject__class_assigned__name',
        'subject__class_assigned__department__name'
    ).annotate(
        total=Count('id'),
        present=Count('id', filter=Q(is_present=True))
    ).order_by('subject__class_assigned__name')
    
    # Subject-wise attendance
    subject_attendance = attendance_records.values(
        'subject__course__name',
        'subject__course__code'
    ).annotate(
        total=Count('id'),
        present=Count('id', filter=Q(is_present=True))
    ).order_by('subject__course__name')
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'selected_department': department_id,
        'departments': Department.objects.all(),
        'overall_percentage': overall_percentage,
        'total_records': total_records,
        'present_records': present_records,
        'class_attendance': class_attendance,
        'subject_attendance': subject_attendance
    }
    
    return render(request, 'administration/attendance_overview.html', context)


@login_required
@user_passes_test(is_admin_user)
def financial_dashboard(request):
    """Financial overview and fee management"""
    current_year = timezone.now().year
    academic_year = f"{current_year}-{current_year + 1}"
    
    # Fee collection statistics
    fee_stats = Fee.objects.filter(
        academic_year=academic_year
    ).aggregate(
        total_fees=Sum('amount'),
        collected_fees=Sum('amount', filter=Q(payment_status='paid')),
        pending_fees=Sum('amount', filter=Q(payment_status__in=['pending', 'partial'])),
        overdue_fees=Sum('amount', filter=Q(payment_status='overdue'))
    )
    
    # Monthly collection data
    monthly_collections = []
    for month in range(1, 13):
        month_data = Fee.objects.filter(
            payment_date__year=current_year,
            payment_date__month=month,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))
        
        monthly_collections.append({
            'month': month,
            'month_name': timezone.datetime(current_year, month, 1).strftime('%B'),
            'amount': month_data['total'] or 0
        })
    
    # Fee type breakdown
    fee_type_breakdown = Fee.objects.filter(
        academic_year=academic_year
    ).values('fee_type').annotate(
        total=Sum('amount'),
        collected=Sum('amount', filter=Q(payment_status='paid'))
    )
    
    # Defaulters list
    defaulters = Fee.objects.filter(
        payment_status__in=['overdue', 'pending'],
        due_date__lt=timezone.now().date()
    ).select_related('student').order_by('due_date')[:20]
    
    context = {
        'academic_year': academic_year,
        'fee_stats': fee_stats,
        'monthly_collections': monthly_collections,
        'fee_type_breakdown': fee_type_breakdown,
        'defaulters': defaulters,
        'collection_percentage': round((fee_stats['collected_fees'] or 0) / (fee_stats['total_fees'] or 1) * 100, 2)
    }
    
    return render(request, 'administration/financial_dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def academic_performance(request):
    """Academic performance analytics"""
    semester = request.GET.get('semester')
    department_id = request.GET.get('department')
    
    # Base queryset
    results = Result.objects.filter(is_published=True)
    
    if semester:
        results = results.filter(exam__subject__class_assigned__semester=semester)
    
    if department_id:
        results = results.filter(
            student__student_profile__department_id=department_id
        )
    
    # Overall performance metrics
    performance_stats = results.aggregate(
        avg_marks=Avg('marks_obtained'),
        total_students=Count('student', distinct=True),
        total_exams=Count('exam', distinct=True),
        pass_count=Count('id', filter=Q(grade__in=['A+', 'A', 'B+', 'B', 'C+', 'C']))
    )
    
    pass_percentage = 0
    if results.count() > 0:
        pass_percentage = round((performance_stats['pass_count'] or 0) / results.count() * 100, 2)
    
    # Grade distribution
    grade_distribution = results.values('grade').annotate(
        count=Count('id')
    ).order_by('grade')
    
    # Subject-wise performance
    subject_performance = results.values(
        'exam__subject__course__name',
        'exam__subject__course__code'
    ).annotate(
        avg_marks=Avg('marks_obtained'),
        total_students=Count('student', distinct=True),
        pass_rate=Avg('marks_obtained__gte', 
                     filter=Q(exam__pass_marks__lte=F('marks_obtained')))
    ).order_by('-avg_marks')
    
    # Top performers
    top_performers = results.values(
        'student__first_name',
        'student__last_name',
        'student__student_profile__roll_number',
        'student__student_profile__department__name'
    ).annotate(
        avg_marks=Avg('marks_obtained')
    ).order_by('-avg_marks')[:10]
    
    context = {
        'selected_semester': semester,
        'selected_department': department_id,
        'departments': Department.objects.all(),
        'semesters': range(1, 9),
        'performance_stats': performance_stats,
        'pass_percentage': pass_percentage,
        'grade_distribution': grade_distribution,
        'subject_performance': subject_performance,
        'top_performers': top_performers
    }
    
    return render(request, 'administration/academic_performance.html', context)


@login_required
@user_passes_test(is_admin_user)
def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        try:
            from accounts.models import User
            
            username = request.POST.get('username')
            # Auto-generate email with @mitwpu.edu.in domain
            email = f"{username}@mitwpu.edu.in"
            
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                user_type='student'
            )
            
            # Update additional fields
            if request.POST.get('phone_number'):
                user.phone_number = request.POST.get('phone_number')
            if request.POST.get('date_of_birth'):
                user.date_of_birth = request.POST.get('date_of_birth')
            if request.POST.get('address'):
                user.address = request.POST.get('address')
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES.get('profile_picture')
            user.save()
            
            # Get department from form
            department_id = request.POST.get('department')
            if not department_id:
                messages.error(request, 'Please select a department.')
                return redirect('administration:dashboard')
            
            department = Department.objects.get(id=department_id)
            
            # Generate unique roll number based on department
            dept_student_count = Student.objects.filter(department=department).count()
            roll_number = f"{department.code}{timezone.now().year}{dept_student_count + 1:04d}"
            admission_number = f"ADM{timezone.now().year}{Student.objects.count() + 1:05d}"
            
            student = Student.objects.create(
                user=user,
                roll_number=roll_number,
                admission_number=admission_number,
                department=department,
                admission_date=timezone.now().date(),
                guardian_name=request.POST.get('guardian_name', 'Not Provided'),
                guardian_phone=request.POST.get('guardian_phone', '0000000000'),
                guardian_address=request.POST.get('guardian_address', 'Not Provided'),
                emergency_contact=request.POST.get('emergency_contact', '0000000000')
            )
            
            messages.success(request, f'✅ Student {user.get_full_name()} added successfully! Roll No: {student.roll_number}, Department: {department.name}')
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
    
    return redirect('administration:dashboard')


@login_required
@user_passes_test(is_admin_user)
def add_teacher(request):
    """Add new teacher"""
    if request.method == 'POST':
        try:
            from accounts.models import User
            
            username = request.POST.get('username')
            # Auto-generate email with @mitwpu.edu.in domain
            email = f"{username}@mitwpu.edu.in"
            
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                user_type='teacher'
            )
            
            # Update additional fields
            if request.POST.get('phone_number'):
                user.phone_number = request.POST.get('phone_number')
            if request.POST.get('date_of_birth'):
                user.date_of_birth = request.POST.get('date_of_birth')
            if request.POST.get('address'):
                user.address = request.POST.get('address')
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES.get('profile_picture')
            user.save()
            
            # Get department from form
            department_id = request.POST.get('department')
            if not department_id:
                messages.error(request, 'Please select a department.')
                return redirect('administration:dashboard')
            
            department = Department.objects.get(id=department_id)
            
            # Generate unique employee ID based on department
            dept_teacher_count = Teacher.objects.filter(department=department).count()
            employee_id = f"{department.code}T{timezone.now().year}{dept_teacher_count + 1:04d}"
            
            # Get qualification from form or default to 'other'
            qualification = request.POST.get('qualification_choice', 'other')
            if not qualification or qualification not in ['bachelor', 'master', 'phd', 'other']:
                qualification = 'other'
            
            teacher = Teacher.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                designation=request.POST.get('designation', 'Assistant Professor'),
                qualification=qualification,
                specialization=request.POST.get('specialization', ''),
                experience_years=int(request.POST.get('experience', 0) or 0),
                employment_type='permanent',
                joining_date=timezone.now().date()
            )
            
            messages.success(request, f'✅ Teacher {user.get_full_name()} added successfully! Employee ID: {teacher.employee_id}, Department: {department.name}')
        except Exception as e:
            messages.error(request, f'Error adding teacher: {str(e)}')
    
    return redirect('administration:dashboard')


@login_required
@user_passes_test(is_admin_user)
def get_user_data(request, user_id):
    """Get user data for editing"""
    try:
        from accounts.models import User
        user = User.objects.get(id=user_id)
        
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '',
            'address': user.address,
            'is_active': user.is_active,
            'user_type': user.user_type,
        }
        
        # Add student-specific data
        if user.user_type == 'student' and hasattr(user, 'student_profile'):
            student = user.student_profile
            data['student_profile'] = {
                'roll_number': student.roll_number,
                'admission_number': student.admission_number,
                'department_id': student.department.id if student.department else None,
                'guardian_name': student.guardian_name,
                'guardian_phone': student.guardian_phone,
                'guardian_address': student.guardian_address,
                'emergency_contact': student.emergency_contact,
            }
        
        # Add teacher-specific data
        if user.user_type == 'teacher' and hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            data['teacher_profile'] = {
                'employee_id': teacher.employee_id,
                'department_id': teacher.department.id if teacher.department else None,
                'designation': teacher.designation,
                'qualification': teacher.qualification,
                'specialization': teacher.specialization,
                'experience_years': teacher.experience_years,
            }
        
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_user)
def edit_user(request):
    """Edit user profile"""
    if request.method == 'POST':
        try:
            from accounts.models import User
            
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            
            # Update basic user information
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number', '')
            user.address = request.POST.get('address', '')
            user.is_active = 'is_active' in request.POST
            
            # Update date of birth if provided
            dob = request.POST.get('date_of_birth')
            if dob:
                user.date_of_birth = dob
            
            # Update profile picture if provided
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES.get('profile_picture')
            
            # Update password if provided
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password and confirm_password:
                if new_password == confirm_password:
                    user.set_password(new_password)
                else:
                    messages.error(request, 'Passwords do not match!')
                    return redirect('administration:users')
            
            user.save()
            
            # Update student-specific information (excluding roll_number, admission_number, department)
            if user.user_type == 'student' and hasattr(user, 'student_profile'):
                student = user.student_profile
                # Only update guardian information - NOT department, roll number, or admission number
                student.guardian_name = request.POST.get('guardian_name', student.guardian_name)
                student.guardian_phone = request.POST.get('guardian_phone', student.guardian_phone)
                student.save()
            
            # Update teacher-specific information (excluding employee_id, department)
            if user.user_type == 'teacher' and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                # Only update mutable fields - NOT employee ID or department
                teacher.designation = request.POST.get('designation', teacher.designation)
                teacher.qualification = request.POST.get('qualification', teacher.qualification)
                teacher.specialization = request.POST.get('specialization', teacher.specialization)
                exp = request.POST.get('experience')
                if exp:
                    teacher.experience_years = int(exp)
                teacher.save()
            
            messages.success(request, f'✅ User {user.get_full_name()} updated successfully!')
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    return redirect('administration:users')