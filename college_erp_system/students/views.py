from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, F
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from academics.models import (
    Timetable, Attendance, Exam, Result, Fee, Subject, Course, AcademicCalendar
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
        Q(target_audience='all_students') |
        Q(target_audience='class', target_class=student.student_class) |
        Q(target_audience='department', target_department=student.department) |
        Q(target_audience='individual_student', target_student=student)
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
    
    # Get current semester from student's class
    current_semester = student.student_class.semester if student.student_class else None
    
    # Get filter parameters
    selected_semester = request.GET.get('semester')
    if selected_semester:
        try:
            selected_semester = int(selected_semester)
        except ValueError:
            selected_semester = current_semester
    else:
        selected_semester = current_semester
    
    # Get all semesters
    semesters = Course.SEMESTER_CHOICES
    
    # Get all attendance records for the logged-in student (for semester-wise breakdown)
    all_attendance_records = Attendance.objects.filter(
        student=request.user
    ).select_related('subject__course', 'subject__course__department', 'subject', 'marked_by').order_by('-date')

    # Get filtered attendance records based on selected semester
    attendance_records = all_attendance_records
    if selected_semester:
        attendance_records = attendance_records.filter(subject__course__semester=selected_semester)

    # Subjects assigned to the student's class, filtered by selected semester
    subjects = Subject.objects.filter(class_assigned=student.student_class).select_related('course', 'course__department')
    
    if selected_semester:
        subjects = subjects.filter(course__semester=selected_semester)

    # Filter by subject if requested
    selected_subject_id = request.GET.get('subject')
    selected_subject = None
    if selected_subject_id:
        try:
            selected_subject = subjects.get(id=selected_subject_id)
        except Subject.DoesNotExist:
            pass

    # Build per-subject rows and aggregates by subject type
    rows = []
    aggregates = {
        'TH': {'present': 0, 'total': 0},
        'PR': {'present': 0, 'total': 0},
        'TU': {'present': 0, 'total': 0},
    }
    
    # Group by semester for semester-wise breakdown (using ALL attendance records)
    semester_attendance = {}
    for semester_num, semester_name in semesters:
        semester_attendance[semester_num] = {
            'name': semester_name,
            'subjects': [],
            'present': 0,
            'total': 0,
            'percentage': 0.0
        }

    # Get all subjects for semester-wise breakdown
    all_subjects = Subject.objects.filter(class_assigned=student.student_class).select_related('course', 'course__department')
    
    # Build semester-wise data from all subjects and all attendance records
    for subject in all_subjects:
        total = all_attendance_records.filter(subject=subject).count()
        present = all_attendance_records.filter(subject=subject, is_present=True).count()
        percentage = round((present / total * 100), 2) if total > 0 else 0.0
        
        # Add to semester-wise data
        sem = subject.course.semester
        if sem in semester_attendance and total > 0:
            semester_attendance[sem]['subjects'].append({
                'subject': subject,
                'present': present,
                'total': total,
                'percentage': percentage,
            })
            semester_attendance[sem]['present'] += present
            semester_attendance[sem]['total'] += total

    # Build rows for filtered subjects (based on selected semester)
    for subject in subjects:
        total = attendance_records.filter(subject=subject).count()
        present = attendance_records.filter(subject=subject, is_present=True).count()
        percentage = round((present / total * 100), 2) if total > 0 else 0.0

        rows.append({
            'subject': subject,
            'subject_type': subject.subject_type,
            'present': present,
            'total': total,
            'percentage': percentage,
            'semester': subject.course.semester,
        })

        if subject.subject_type in aggregates:
            aggregates[subject.subject_type]['present'] += present
            aggregates[subject.subject_type]['total'] += total

    # Calculate percentages for semester-wise data
    for sem in semester_attendance:
        sem_data = semester_attendance[sem]
        if sem_data['total'] > 0:
            sem_data['percentage'] = round((sem_data['present'] / sem_data['total'] * 100), 2)

    # Compute percentages for aggregates
    def pct(p, t):
        return round((p / t * 100), 2) if t > 0 else 0.0

    summary = {
        'theory': {
            'present': aggregates['TH']['present'],
            'total': aggregates['TH']['total'],
            'percentage': pct(aggregates['TH']['present'], aggregates['TH']['total']),
        },
        'practical': {
            'present': aggregates['PR']['present'],
            'total': aggregates['PR']['total'],
            'percentage': pct(aggregates['PR']['present'], aggregates['PR']['total']),
        },
        'tutorial': {
            'present': aggregates['TU']['present'],
            'total': aggregates['TU']['total'],
            'percentage': pct(aggregates['TU']['present'], aggregates['TU']['total']),
        },
    }

    overall_present = sum(a['present'] for a in aggregates.values())
    overall_total = sum(a['total'] for a in aggregates.values())
    summary['overall'] = {
        'present': overall_present,
        'total': overall_total,
        'percentage': pct(overall_present, overall_total),
    }

    # Get recent attendance records (last 20 records)
    recent_records = attendance_records[:20]
    if selected_subject:
        recent_records = attendance_records.filter(subject=selected_subject)[:20]

    context = {
        'student': student,
        'rows': rows,
        'summary': summary,
        'recent_records': recent_records,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'semesters': semesters,
        'selected_semester': selected_semester,
        'current_semester': current_semester,
        'semester_attendance': semester_attendance,
    }
    return render(request, 'students/attendance.html', context)

@login_required
def exams(request):
    """Display upcoming and past exams with results"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    # Get all exams for student's class
    upcoming_exams = Exam.objects.filter(
        subject__class_assigned=student.student_class,
        date__gte=timezone.now()
    ).select_related('subject__course', 'subject__teacher').order_by('date')
    
    past_exams = Exam.objects.filter(
        subject__class_assigned=student.student_class,
        date__lt=timezone.now()
    ).select_related('subject__course', 'subject__teacher').order_by('-date')
    
    # Get student results for past exams
    from academics.models import Result
    results_map = {}
    student_results = Result.objects.filter(
        student=request.user,
        exam__in=past_exams
    ).select_related('exam')
    
    for result in student_results:
        results_map[result.exam.id] = result
    
    # Add results to past exams
    past_exams_with_results = []
    for exam in past_exams:
        result = results_map.get(exam.id)
        past_exams_with_results.append({
            'exam': exam,
            'result': result,
        })
    
    context = {
        'student': student,
        'upcoming_exams': upcoming_exams,
        'past_exams_with_results': past_exams_with_results,
    }
    return render(request, 'students/exams.html', context)

@login_required
def results(request):
    """Display exam results and grades"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    # Get all results (published and unpublished)
    results = Result.objects.filter(
        student=request.user
    ).select_related('exam__subject__course', 'exam__created_by').order_by('-exam__date')
    
    # Separate published and unpublished results
    published_results = results.filter(is_published=True)
    unpublished_results = results.filter(is_published=False)
    
    # Calculate overall performance (only published)
    total_marks = sum([r.exam.total_marks for r in published_results])
    obtained_marks = sum([r.marks_obtained or 0 for r in published_results])
    overall_percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    
    # Count pass/fail
    passed = published_results.filter(marks_obtained__gte=models.F('exam__pass_marks')).count()
    failed = published_results.exclude(marks_obtained__gte=models.F('exam__pass_marks')).count()
    
    context = {
        'student': student,
        'published_results': published_results,
        'unpublished_results': unpublished_results,
        'results': results,
        'overall_percentage': round(overall_percentage, 1),
        'passed': passed,
        'failed': failed,
        'total_exams': len(published_results),
    }
    return render(request, 'students/results.html', context)

@login_required
def fees(request):
    """Display fee details and payment status"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    from academics.models import PaymentMethod, Transaction
    import uuid
    
    student = request.user.student_profile
    
    all_fees = Fee.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    pending_fees = all_fees.filter(payment_status__in=['pending', 'overdue'])
    paid_fees = all_fees.filter(payment_status='paid')
    partial_fees = all_fees.filter(payment_status='partial')
    
    # Calculate totals
    total_pending = sum([fee.amount for fee in pending_fees])
    total_paid = sum([fee.amount for fee in paid_fees])
    total_partial = sum([fee.amount for fee in partial_fees])
    total_fees_amount = total_pending + total_paid + total_partial
    
    # Get available payment methods
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Handle payment processing
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        payment_method_id = request.POST.get('payment_method_id')
        amount = request.POST.get('amount')
        reference_number = request.POST.get('reference_number', '')
        
        try:
            fee = Fee.objects.get(id=fee_id, student=request.user)
            payment_method = PaymentMethod.objects.get(id=payment_method_id) if payment_method_id else None
            
            if fee.payment_status == 'paid':
                messages.info(request, "This fee has already been paid.")
            else:
                try:
                    amount_decimal = Decimal(amount)
                except:
                    messages.error(request, "Invalid amount entered.")
                    return redirect('students:fees')
                
                # Create transaction
                transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
                transaction = Transaction.objects.create(
                    fee=fee,
                    payment_method=payment_method,
                    amount=amount_decimal,
                    status='completed',
                    transaction_id=transaction_id,
                    reference_number=reference_number,
                    completed_at=timezone.now()
                )
                
                # Update fee status based on amount
                if amount_decimal >= fee.amount:
                    fee.payment_status = 'paid'
                    fee.payment_date = timezone.now().date()
                    messages.success(request, f"✅ Full payment of ₹{amount_decimal} successful!\nTransaction ID: {transaction_id}\nReceipt has been generated.")
                elif amount_decimal > 0:
                    fee.payment_status = 'partial'
                    messages.success(request, f"✅ Partial payment of ₹{amount_decimal} received!\nTransaction ID: {transaction_id}\nRemaining: ₹{fee.amount - amount_decimal}")
                
                fee.payment_method = payment_method.get_method_type_display() if payment_method else 'Online'
                fee.transaction_id = transaction_id
                fee.save()
        
        except Fee.DoesNotExist:
            messages.error(request, "Fee not found.")
        except PaymentMethod.DoesNotExist:
            messages.error(request, "Payment method not found.")
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
        
        return redirect('students:fees')
    
    # Get transaction history for paid fees
    transactions = Transaction.objects.filter(
        fee__student=request.user
    ).select_related('payment_method').order_by('-created_at')[:20]
    
    context = {
        'student': student,
        'all_fees': all_fees,
        'pending_fees': pending_fees,
        'paid_fees': paid_fees,
        'partial_fees': partial_fees,
        'total_pending': total_pending,
        'total_paid': total_paid,
        'total_partial': total_partial,
        'total_fees_amount': total_fees_amount,
        'payment_methods': payment_methods,
        'transactions': transactions,
    }
    return render(request, 'students/fees.html', context)


@login_required
def fee_receipt(request, fee_id):
    """Generate and display fee payment receipt"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    try:
        fee = Fee.objects.get(id=fee_id, student=request.user)
    except Fee.DoesNotExist:
        messages.error(request, "Fee receipt not found.")
        return redirect('students:fees')
    
    context = {
        'student': request.user.student_profile,
        'fee': fee,
    }
    return render(request, 'students/fee_receipt.html', context)

@login_required
def notifications(request):
    """Display notifications for student"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    notifications = Notification.objects.filter(
        Q(target_audience='all') |
        Q(target_audience='all_students') |
        Q(target_audience='class', target_class=student.student_class) |
        Q(target_audience='department', target_department=student.department) |
        Q(target_audience='individual_student', target_student=student)
    ).order_by('-created_at')
    
    context = {
        'student': student,
        'notifications': notifications,
    }
    return render(request, 'students/notifications.html', context)

@login_required
def academic_calendar(request):
    """Display academic calendar for the institution"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    student = request.user.student_profile
    
    # Get academic calendar events
    calendar_events = AcademicCalendar.objects.all().order_by('start_date')
    
    context = {
        'student': student,
        'calendar_events': calendar_events,
    }
    return render(request, 'students/academic_calendar.html', context)
