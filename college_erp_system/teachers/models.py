from django.db import models
from django.conf import settings
from academics.models import Department

class Teacher(models.Model):
    QUALIFICATION_CHOICES = [
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', 'Ph.D.'),
        ('other', 'Other'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('visiting', 'Visiting'),
        ('guest', 'Guest Faculty'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    office_room = models.CharField(max_length=50, blank=True)
    office_hours = models.CharField(max_length=100, blank=True)
    research_interests = models.TextField(blank=True)
    publications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
