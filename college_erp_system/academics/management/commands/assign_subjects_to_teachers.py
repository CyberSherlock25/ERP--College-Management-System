from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Subject, Class
from teachers.models import Teacher

User = get_user_model()

class Command(BaseCommand):
    help = 'Assign Semester 1 subjects to teachers'

    def handle(self, *args, **options):
        # Get all Semester 1 classes
        semester1_classes = Class.objects.filter(semester=1)
        
        if not semester1_classes.exists():
            self.stdout.write(self.style.ERROR('No Semester 1 classes found!'))
            return

        # Get all teachers
        teachers = Teacher.objects.filter(is_active=True).select_related('user')
        
        if not teachers.exists():
            self.stdout.write(self.style.ERROR('No active teachers found!'))
            return

        # Get all Semester 1 subjects without teachers
        subjects = Subject.objects.filter(
            class_assigned__semester=1,
            teacher__isnull=True
        ).select_related('course', 'class_assigned')

        if not subjects.exists():
            self.stdout.write(self.style.WARNING('All Semester 1 subjects already have teachers assigned!'))
            # Show current assignments
            all_subjects = Subject.objects.filter(class_assigned__semester=1).select_related('course', 'teacher')
            for subject in all_subjects:
                teacher_name = subject.teacher.get_full_name() if subject.teacher else 'No teacher'
                self.stdout.write(f'  {subject.course.code}: {subject.course.name} - Teacher: {teacher_name}')
            return

        # Assign subjects to teachers in round-robin fashion
        teacher_list = list(teachers)
        assigned_count = 0

        for idx, subject in enumerate(subjects):
            # Assign to teacher in round-robin
            teacher = teacher_list[idx % len(teacher_list)]
            subject.teacher = teacher.user
            subject.save()
            assigned_count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Assigned {subject.course.code}: {subject.course.name} to {teacher.user.get_full_name()}'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Successfully assigned {assigned_count} subjects to teachers!'
        ))

        # Show summary
        self.stdout.write('')
        self.stdout.write('Subject-Teacher Assignments:')
        all_subjects = Subject.objects.filter(class_assigned__semester=1).select_related('course', 'teacher', 'class_assigned')
        for subject in all_subjects:
            teacher_name = subject.teacher.get_full_name() if subject.teacher else 'No teacher'
            self.stdout.write(f'  {subject.course.code}: {subject.course.name} ({subject.class_assigned.name}) - Teacher: {teacher_name}')

