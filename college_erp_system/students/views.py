from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from academics.models import (
    Timetable, Attendance, Exam, Result, Fee, Subject
)
from .models import Student, Notification

@login_required
def dashboard(request):
    """Student dashboard with overview"""
    if not request.user.is_student:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('accounts:login')
    
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact administrator.")
        return redirect('accounts:login')
    
    # Get recent attendance percentage
    total_attendance = Attendance.objects.filter(student=request.user).count()
    present_attendance = Attendance.objects.filter(student=request.user, is_present=True).count()
    attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
    
    # Get upcoming exams
    upcoming_exams = Exam.objects.filter(
        subject__class_assigned=student.student_class,
        date__gte=timezone.now()
    ).order_by('date')[:5]
    
    # Get pending fees
    pending_fees = Fee.objects.filter(
        student=request.user,
        payment_status__in=['pending', 'overdue']
    ).order_by('due_date')
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        Q(target_audience='all') |
        Q(target_audience='class', target_class=student.student_class) |
        Q(target_audience='department', target_department=student.department) |
        Q(target_audience='individual', target_student=student)
    ).order_by('-created_at')[:5]
    
    context = {
        'student': student,
        'attendance_percentage': round(attendance_percentage, 1),
        'upcoming_exams': upcoming_exams,
        'pending_fees': pending_fees,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def timetable(request):
    """Display student's class timetable"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    if not student.student_class:
        messages.warning(request, "You are not assigned to any class. Please contact administrator.")
        return render(request, 'students/timetable.html')
    
    timetable = Timetable.objects.filter(
        class_assigned=student.student_class
    ).select_related('subject__course', 'time_slot').order_by(
        'time_slot__day', 'time_slot__start_time'
    )
    
    # Organize timetable by day
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    organized_timetable = {}
    
    for day in days:
        organized_timetable[day] = timetable.filter(time_slot__day=day)
    
    context = {
        'student': student,
        'organized_timetable': organized_timetable,
        'days': days,
    }
    return render(request, 'students/timetable.html', context)

@login_required
def attendance(request):
    """Display student's attendance records"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    # Get attendance records for current semester
    attendance_records = Attendance.objects.filter(
        student=request.user
    ).select_related('subject__course').order_by('-date')
    
    # Calculate attendance percentage by subject
    subjects = Subject.objects.filter(class_assigned=student.student_class)
    subject_attendance = {}
    
    for subject in subjects:
        total = attendance_records.filter(subject=subject).count()
        present = attendance_records.filter(subject=subject, is_present=True).count()
        percentage = (present / total * 100) if total > 0 else 0
        subject_attendance[subject] = {
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': round(percentage, 1)
        }
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'subject_attendance': subject_attendance,
    }
    return render(request, 'students/attendance.html', context)

@login_required
def exams(request):
    """Display upcoming and past exams"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    upcoming_exams = Exam.objects.filter(
        subject__class_assigned=student.student_class,
        date__gte=timezone.now()
    ).select_related('subject__course').order_by('date')
    
    past_exams = Exam.objects.filter(
        subject__class_assigned=student.student_class,
        date__lt=timezone.now()
    ).select_related('subject__course').order_by('-date')
    
    context = {
        'student': student,
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
    }
    return render(request, 'students/exams.html', context)

@login_required
def results(request):
    """Display exam results"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    results = Result.objects.filter(
        student=request.user,
        is_published=True
    ).select_related('exam__subject__course').order_by('-exam__date')
    
    # Calculate overall performance
    total_marks = sum([r.exam.total_marks for r in results])
    obtained_marks = sum([r.marks_obtained or 0 for r in results])
    overall_percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    
    context = {
        'student': student,
        'results': results,
        'overall_percentage': round(overall_percentage, 1),
    }
    return render(request, 'students/results.html', context)

@login_required
def fees(request):
    """Display fee details and payment status"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    all_fees = Fee.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    pending_fees = all_fees.filter(payment_status__in=['pending', 'overdue'])
    paid_fees = all_fees.filter(payment_status='paid')
    
    # Calculate totals
    total_pending = sum([fee.amount for fee in pending_fees])
    total_paid = sum([fee.amount for fee in paid_fees])
    
    context = {
        'student': student,
        'all_fees': all_fees,
        'pending_fees': pending_fees,
        'paid_fees': paid_fees,
        'total_pending': total_pending,
        'total_paid': total_paid,
    }
    return render(request, 'students/fees.html', context)

@login_required
def notifications(request):
    """Display notifications for student"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    notifications = Notification.objects.filter(
        Q(target_audience='all') |
        Q(target_audience='class', target_class=student.student_class) |
        Q(target_audience='department', target_department=student.department) |
        Q(target_audience='individual', target_student=student)
    ).order_by('-created_at')
    
    context = {
        'student': student,
        'notifications': notifications,
    }
    return render(request, 'students/notifications.html', context)
