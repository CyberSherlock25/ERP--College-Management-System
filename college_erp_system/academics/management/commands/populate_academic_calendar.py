from django.core.management.base import BaseCommand
from academics.models import AcademicCalendar
from datetime import date

class Command(BaseCommand):
    help = 'Populate Academic Calendar for 2025-2026'

    def handle(self, *args, **kwargs):
        # Clear existing calendar for 2025-2026
        AcademicCalendar.objects.filter(academic_year='2025-2026').delete()
        
        # Academic Calendar data from the provided image
        calendar_events = [
            {
                'title': 'Commencement of Term',
                'start_date': date(2025, 7, 7),
                'end_date': date(2025, 7, 7),
                'remarks': '',
                'category': 'term',
            },
            {
                'title': 'Induction',
                'start_date': date(2025, 7, 7),
                'end_date': date(2025, 7, 8),
                'remarks': '02 Days',
                'category': 'induction',
            },
            {
                'title': 'Academic Instruction Duration (regular classes)',
                'start_date': date(2025, 7, 8),
                'end_date': date(2024, 11, 18),  # Note: Image shows 18th Nov 2024, likely should be 2025
                'remarks': '',
                'category': 'instruction',
                'instructional_days': 93,
            },
            {
                'title': 'Mid Term Exam',
                'start_date': date(2025, 9, 29),
                'end_date': date(2025, 10, 10),
                'remarks': '',
                'category': 'exam_mid',
            },
            {
                'title': 'Diwali Vacation',
                'start_date': date(2025, 10, 18),
                'end_date': date(2025, 10, 25),
                'remarks': '',
                'category': 'vacation',
            },
            {
                'title': 'Last Instructional Day',
                'start_date': date(2025, 12, 12),
                'end_date': date(2025, 12, 12),
                'remarks': '93 Instructional Days',
                'category': 'instruction',
                'instructional_days': 93,
            },
            {
                'title': 'Term End Exam (Backlog)',
                'start_date': date(2025, 11, 19),
                'end_date': date(2025, 11, 30),
                'remarks': '10 Working Days',
                'category': 'exam_backlog',
                'working_days': 10,
            },
            {
                'title': 'Term End Exam (Regular)',
                'start_date': date(2025, 12, 1),
                'end_date': date(2025, 12, 22),
                'remarks': '22 Working Days',
                'category': 'exam_regular',
                'working_days': 22,
            },
            {
                'title': 'Winter Vacation',
                'start_date': date(2025, 12, 23),
                'end_date': date(2026, 1, 4),
                'remarks': '',
                'category': 'vacation',
            },
        ]
        
        created_count = 0
        for event_data in calendar_events:
            event_data['academic_year'] = '2025-2026'
            AcademicCalendar.objects.create(**event_data)
            created_count += 1
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} academic calendar events for 2025-2026'
            )
        )
