from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Department, Course, Class, Subject
from teachers.models import Teacher
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Add Semester 1 subjects: DCN, Python, Java, ADBMS, Peace, Yoga, Research Methodology'

    def handle(self, *args, **options):
        # Get or create Computer Science department
        cs_dept, created = Department.objects.get_or_create(
            code='CS',
            defaults={
                'name': 'Computer Science',
                'description': 'Department of Computer Science'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created department: {cs_dept.name}'))
        else:
            self.stdout.write(f'Using existing department: {cs_dept.name}')

        # Get or create General Education department for Peace, Yoga
        gen_dept, created = Department.objects.get_or_create(
            code='GEN',
            defaults={
                'name': 'General Education',
                'description': 'General Education Department'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created department: {gen_dept.name}'))
        else:
            self.stdout.write(f'Using existing department: {gen_dept.name}')

        # Get or create a teacher for Semester 1 classes
        # First, try to get an existing teacher
        teacher_user = None
        teacher = Teacher.objects.first()
        
        if teacher:
            teacher_user = teacher.user
            self.stdout.write(f'Using existing teacher: {teacher_user.get_full_name()}')
        else:
            # Create a teacher if none exists
            teacher_user, created = User.objects.get_or_create(
                username='teacher1',
                defaults={
                    'email': 'teacher1@college.edu',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'user_type': 'teacher'
                }
            )
            if created:
                teacher_user.set_password('teacher123')
                teacher_user.save()
                teacher = Teacher.objects.create(
                    user=teacher_user,
                    employee_id='EMP001',
                    department=cs_dept,
                    designation='Assistant Professor',
                    qualification='master',
                    specialization='Computer Science',
                    experience_years=5,
                    employment_type='permanent',
                    joining_date=date(2020, 1, 1)
                )
                self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher_user.get_full_name()}'))
            else:
                self.stdout.write(f'Using existing teacher user: {teacher_user.username}')

        # Get or create Semester 1 classes for CS department
        # Try to find any existing Semester 1 class
        semester1_class = Class.objects.filter(department=cs_dept, semester=1).first()
        
        if not semester1_class:
            # Create Semester 1 class
            semester1_class = Class.objects.create(
                name='CS Semester 1 A',
                department=cs_dept,
                semester=1,
                section='A',
                academic_year='2024-2025',
                class_teacher=teacher_user,
                max_strength=60
            )
            self.stdout.write(self.style.SUCCESS(f'Created class: {semester1_class.name}'))
        else:
            self.stdout.write(f'Using existing class: {semester1_class.name}')

        # Define Semester 1 courses
        courses_data = [
            # CS Department courses
            {
                'code': 'CS101',
                'name': 'Data Communication and Networks',
                'department': cs_dept,
                'semester': 1,
                'credits': 4,
                'description': 'Introduction to data communication and computer networks',
                'subject_type': 'TH'  # Theory
            },
            {
                'code': 'CS102',
                'name': 'Python Programming',
                'department': cs_dept,
                'semester': 1,
                'credits': 4,
                'description': 'Python programming fundamentals and applications',
                'subject_type': 'TH'  # Theory
            },
            {
                'code': 'CS103',
                'name': 'Java Programming',
                'department': cs_dept,
                'semester': 1,
                'credits': 4,
                'description': 'Object-oriented programming using Java',
                'subject_type': 'TH'  # Theory
            },
            {
                'code': 'CS104',
                'name': 'Advanced Database Management Systems',
                'department': cs_dept,
                'semester': 1,
                'credits': 4,
                'description': 'Advanced concepts in database design and management',
                'subject_type': 'TH'  # Theory
            },
            # General Education courses
            {
                'code': 'GEN101',
                'name': 'Peace Studies',
                'department': gen_dept,
                'semester': 1,
                'credits': 2,
                'description': 'Peace and conflict resolution studies',
                'subject_type': 'TH'  # Theory
            },
            {
                'code': 'GEN102',
                'name': 'Yoga',
                'department': gen_dept,
                'semester': 1,
                'credits': 1,
                'description': 'Yoga and wellness practices',
                'subject_type': 'PR'  # Practical
            },
            {
                'code': 'CS105',
                'name': 'Research Methodology',
                'department': cs_dept,
                'semester': 1,
                'credits': 3,
                'description': 'Research methods and academic writing',
                'subject_type': 'TH'  # Theory
            },
        ]

        # Create courses and subjects
        created_count = 0
        updated_count = 0

        for course_data in courses_data:
            # Extract subject_type before creating course
            subject_type = course_data.pop('subject_type')
            
            # Create or get course
            course, course_created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults=course_data
            )
            
            if course_created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.code} - {course.name}'))
            else:
                # Update course if it exists
                for key, value in course_data.items():
                    setattr(course, key, value)
                course.save()
                self.stdout.write(f'Updated course: {course.code} - {course.name}')

            # Create or get subject for the class
            subject, subject_created = Subject.objects.get_or_create(
                course=course,
                class_assigned=semester1_class,
                defaults={
                    'teacher': teacher_user,
                    'subject_type': subject_type
                }
            )

            if subject_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created subject: {course.name} for class {semester1_class.name}'
                ))
            else:
                # Update subject if it exists
                if not subject.teacher:
                    subject.teacher = teacher_user
                subject.subject_type = subject_type
                subject.save()
                updated_count += 1
                self.stdout.write(
                    f'Updated subject: {course.name} for class {semester1_class.name}'
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Successfully added/updated Semester 1 subjects!'
        ))
        self.stdout.write(f'  Created: {created_count} subjects')
        self.stdout.write(f'  Updated: {updated_count} subjects')
        self.stdout.write('')
        self.stdout.write('Semester 1 Subjects:')
        subjects = Subject.objects.filter(class_assigned=semester1_class).select_related('course')
        for subject in subjects:
            self.stdout.write(f'  - {subject.course.code}: {subject.course.name} ({subject.get_subject_type_display()})')

