from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
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
    return user.is_authenticated and (user.is_staff or user.is_superuser)


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
    """Manage students and teachers"""
    user_type = request.GET.get('type', 'students')
    search_query = request.GET.get('search', '')
    
    context = {'user_type': user_type, 'search_query': search_query}
    
    if user_type == 'students':
        students = Student.objects.filter(is_active=True).select_related('user', 'department')
        
        if search_query:
            students = students.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(roll_number__icontains=search_query) |
                Q(admission_number__icontains=search_query)
            )
        
        context['students'] = students
        context['total_students'] = students.count()
    
    elif user_type == 'teachers':
        teachers = Teacher.objects.filter(is_active=True).select_related('user', 'department')
        
        if search_query:
            teachers = teachers.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(designation__icontains=search_query)
            )
        
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
