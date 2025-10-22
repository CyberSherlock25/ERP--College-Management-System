from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Update all user emails to username@mitwpu.edu.in format'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            new_email = f"{user.username}@mitwpu.edu.in"
            if user.email != new_email:
                user.email = new_email
                user.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {user.username}: {new_email}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully updated {updated_count} user email(s)')
        )
