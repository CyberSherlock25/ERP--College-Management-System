from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import TeacherTimetable, TimeSlot, Subject
from datetime import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate Teacher Timetable based on provided schedule'

    def add_arguments(self, parser):
        parser.add_argument(
            '--teacher-username',
            type=str,
            help='Username of the teacher to create timetable for',
            default='bala.reddye'
        )

    def handle(self, *args, **kwargs):
        teacher_username = kwargs['teacher_username']
        
        try:
            teacher = User.objects.get(username=teacher_username, is_teacher=True)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Teacher with username "{teacher_username}" not found')
            )
            return
        
        # Clear existing timetable for this teacher
        TeacherTimetable.objects.filter(teacher=teacher, academic_year='2025-2026').delete()
        
        # Create time slots based on the timetable image provided
        time_slots_data = [
            {'day': 'monday', 'start_time': time(10, 30), 'end_time': time(11, 30)},
            {'day': 'monday', 'start_time': time(11, 30), 'end_time': time(12, 30)},
            {'day': 'monday', 'start_time': time(12, 30), 'end_time': time(13, 30)},
            {'day': 'monday', 'start_time': time(13, 30), 'end_time': time(14, 30)},
            {'day': 'monday', 'start_time': time(14, 30), 'end_time': time(15, 30)},
            {'day': 'monday', 'start_time': time(15, 30), 'end_time': time(16, 30)},
            {'day': 'monday', 'start_time': time(16, 30), 'end_time': time(17, 30)},
            
            {'day': 'tuesday', 'start_time': time(10, 30), 'end_time': time(11, 30)},
            {'day': 'tuesday', 'start_time': time(11, 30), 'end_time': time(12, 30)},
            {'day': 'tuesday', 'start_time': time(12, 30), 'end_time': time(13, 30)},
            {'day': 'tuesday', 'start_time': time(13, 30), 'end_time': time(14, 30)},
            {'day': 'tuesday', 'start_time': time(14, 30), 'end_time': time(15, 30)},
            {'day': 'tuesday', 'start_time': time(15, 30), 'end_time': time(16, 30)},
            
            {'day': 'wednesday', 'start_time': time(11, 30), 'end_time': time(12, 30)},
            {'day': 'wednesday', 'start_time': time(12, 30), 'end_time': time(13, 30)},
            {'day': 'wednesday', 'start_time': time(15, 30), 'end_time': time(16, 30)},
            
            {'day': 'thursday', 'start_time': time(11, 30), 'end_time': time(12, 30)},
            {'day': 'thursday', 'start_time': time(12, 30), 'end_time': time(13, 30)},
            {'day': 'thursday', 'start_time': time(15, 30), 'end_time': time(16, 30)},
            
            {'day': 'friday', 'start_time': time(11, 30), 'end_time': time(12, 30)},
            {'day': 'friday', 'start_time': time(15, 30), 'end_time': time(16, 30)},
        ]
        
        # Create or get time slots
        for slot_data in time_slots_data:
            TimeSlot.objects.get_or_create(**slot_data)
        
        # Get subjects taught by the teacher (you'll need to adjust this based on actual subjects)
        subjects = Subject.objects.filter(teacher=teacher)
        
        if not subjects.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'No subjects found for teacher {teacher.get_full_name()}. '
                    f'Please assign subjects first.'
                )
            )
            return
        
        # Timetable mapping based on the provided image
        # Format: (day, start_time, end_time, subject_code_pattern, room_number)
        timetable_mapping = [
            # Monday
            ('monday', time(10, 30), time(11, 30), 'LEWT - VY 427', 'VY 427'),
            ('monday', time(14, 30), time(15, 30), 'PP - VY 515', 'VY 515'),
            
            # Tuesday
            ('tuesday', time(10, 30), time(11, 30), 'LEWT - VY 427', 'VY 427'),
            ('tuesday', time(11, 30), time(12, 30), 'PP - VY 325', 'VY 325'),
            ('tuesday', time(14, 30), time(15, 30), 'PP - VY 515', 'VY 515'),
            ('tuesday', time(15, 30), time(16, 30), 'RJS - VY 403', 'VY 403'),
            
            # Wednesday
            ('wednesday', time(11, 30), time(12, 30), 'PP - VY 515', 'VY 515'),
            ('wednesday', time(12, 30), time(13, 30), 'PP - VY 325', 'VY 325'),
            ('wednesday', time(15, 30), time(16, 30), 'RJS - VY 403', 'VY 403'),
            
            # Thursday
            ('thursday', time(11, 30), time(12, 30), 'PP - VY 515', 'VY 515'),
            ('thursday', time(12, 30), time(13, 30), 'PP - VY 325', 'VY 325'),
            ('thursday', time(15, 30), time(16, 30), 'RJS - VY 403', 'VY 403'),
            
            # Friday
            ('friday', time(11, 30), time(12, 30), 'PP - VY 325', 'VY 325'),
            ('friday', time(15, 30), time(16, 30), 'RJS - VY 403', 'VY 403'),
        ]
        
        created_count = 0
        for day, start_time, end_time, subject_pattern, room in timetable_mapping:
            # Find the appropriate subject (simplified - you may need better matching)
            subject = subjects.first()  # Using first subject as fallback
            
            # Get or create the time slot
            time_slot, created = TimeSlot.objects.get_or_create(
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created time slot: {day} {start_time}-{end_time}'
                    )
                )
            
            # Create teacher timetable entry
            try:
                TeacherTimetable.objects.create(
                    teacher=teacher,
                    subject=subject,
                    time_slot=time_slot,
                    room_number=room,
                    academic_year='2025-2026'
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Added: {day.title()} {start_time} - {subject_pattern} in {room}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Error creating entry: {day} {start_time} - {str(e)}'
                    )
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} timetable entries for {teacher.get_full_name()}'
            )
        )
