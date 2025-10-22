from django.db import models
from django.conf import settings
from academics.models import Class, Department

class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    roll_number = models.CharField(max_length=20, unique=True)
    admission_number = models.CharField(max_length=20, unique=True)
    student_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    admission_date = models.DateField()
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)
    guardian_email = models.EmailField(blank=True)
    guardian_address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"
    
    @property
    def current_semester(self):
        return self.student_class.semester if self.student_class else None

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('general', 'General'),
        ('academic', 'Academic'),
        ('exam', 'Exam'),
        ('fee', 'Fee'),
        ('event', 'Event'),
        ('announcement', 'Announcement'),
        ('alert', 'Alert'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    target_audience = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All'),
            ('all_students', 'All Students'),
            ('all_teachers', 'All Teachers'),
            ('class', 'Specific Class'),
            ('department', 'Specific Department'),
            ('individual_student', 'Individual Student'),
            ('individual_teacher', 'Individual Teacher'),
        ],
        default='all'
    )
    target_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    target_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_urgent = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
