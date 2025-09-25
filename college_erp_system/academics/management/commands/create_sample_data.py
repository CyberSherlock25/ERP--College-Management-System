from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Department, Course, Class
from students.models import Student
from teachers.models import Teacher
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create departments
        cs_dept = Department.objects.get_or_create(
            name='Computer Science',
            code='CS',
            description='Department of Computer Science'
        )[0]
        
        math_dept = Department.objects.get_or_create(
            name='Mathematics',
            code='MATH',
            description='Department of Mathematics'
        )[0]
        
        # Create sample admin user
        admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@college.edu',
            first_name='System',
            last_name='Administrator',
            user_type='admin'
        )
        
        # Create sample teacher
        teacher_user = User.objects.create_user(
            username='teacher1',
            password='teacher123',
            email='teacher@college.edu',
            first_name='John',
            last_name='Doe',
            user_type='teacher'
        )
        
        teacher = Teacher.objects.create(
            user=teacher_user,
            employee_id='EMP001',
            department=cs_dept,
            designation='Assistant Professor',
            qualification='master',
            specialization='Software Engineering',
            experience_years=5,
            employment_type='permanent',
            joining_date=date(2020, 1, 1)
        )
        
        # Create sample student
        student_user = User.objects.create_user(
            username='student1',
            password='student123',
            email='student@college.edu',
            first_name='Jane',
            last_name='Smith',
            user_type='student'
        )
        
        # Create a class
        student_class = Class.objects.create(
            name='CS Semester 1 A',
            department=cs_dept,
            semester=1,
            section='A',
            academic_year='2024-2025',
            class_teacher=teacher_user,
            max_strength=60
        )
        
        # Create student profile
        student = Student.objects.create(
            user=student_user,
            roll_number='CS001',
            admission_number='ADM2024001',
            student_class=student_class,
            department=cs_dept,
            admission_date=date(2024, 1, 1),
            guardian_name='Mr. Robert Smith',
            guardian_phone='1234567890',
            guardian_email='guardian@email.com',
            guardian_address='123 Main Street, City, State',
            emergency_contact='0987654321',
            blood_group='O+',
        )
        
        # Create some courses
        Course.objects.get_or_create(
            name='Programming Fundamentals',
            code='CS101',
            department=cs_dept,
            semester=1,
            credits=4,
            description='Introduction to programming concepts'
        )
        
        Course.objects.get_or_create(
            name='Mathematics I',
            code='MATH101',
            department=math_dept,
            semester=1,
            credits=3,
            description='Basic mathematics for engineering'
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('Demo Users:')
        self.stdout.write('  Admin: admin/admin123')
        self.stdout.write('  Teacher: teacher1/teacher123')
        self.stdout.write('  Student: student1/student123')
