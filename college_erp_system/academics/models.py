from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='headed_departments'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    description = models.TextField(blank=True)
    syllabus = models.FileField(upload_to='syllabi/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Class(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=Course.SEMESTER_CHOICES)
    section = models.CharField(max_length=10, default='A')
    academic_year = models.CharField(max_length=9)  # e.g., "2023-2024"
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_classes'
    )
    max_strength = models.IntegerField(default=60)
    
    class Meta:
        unique_together = ['department', 'semester', 'section', 'academic_year']
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return f"{self.department.code} - Sem {self.semester} - {self.section}"

class Subject(models.Model):
    # Subject delivery type to differentiate Theory/Practical/Tutorial
    SUBJECT_TYPE_CHOICES = [
        ('TH', 'Theory'),
        ('PR', 'Practical'),
        ('TU', 'Tutorial'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_subjects'
    )
    subject_type = models.CharField(max_length=2, choices=SUBJECT_TYPE_CHOICES, default='TH')
    
    class Meta:
        unique_together = ['course', 'class_assigned']
    
    def __str__(self):
        return f"{self.course.name} - {self.class_assigned}"

class TimeSlot(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['day', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.get_day_display()} ({self.start_time} - {self.end_time})"

class Timetable(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        unique_together = ['class_assigned', 'time_slot']
    
    def __str__(self):
        return f"{self.class_assigned} - {self.subject.course.name} - {self.time_slot}"

class Attendance(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    remarks = models.CharField(max_length=100, blank=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.username} - {self.subject.course.name} - {self.date} - {status}"

class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('midterm', 'Mid-term Exam'),
        ('final', 'Final Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
    ]
    
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.DurationField()  # Duration of exam
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    pass_marks = models.IntegerField(validators=[MinValueValidator(1)])
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject.course.name}"

class Result(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_results'
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.name} - {self.marks_obtained}/{self.exam.total_marks}"
    
    def calculate_grade(self):
        if self.marks_obtained is None:
            return ''
        
        percentage = (self.marks_obtained / self.exam.total_marks) * 100
        
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        else:
            return 'F'
    
    def save(self, *args, **kwargs):
        if self.marks_obtained is not None:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

class Fee(models.Model):
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Laboratory Fee'),
        ('exam', 'Examination Fee'),
        ('development', 'Development Fee'),
        ('other', 'Other Fee'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partially Paid'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fees'
    )
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    academic_year = models.CharField(max_length=9)
    semester = models.IntegerField(choices=Course.SEMESTER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.get_fee_type_display()} - {self.amount}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.payment_status != 'paid'
