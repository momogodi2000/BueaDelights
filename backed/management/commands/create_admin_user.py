from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.utils import timezone
from backed.models import UserProfile  # Using your actual app name from the error logs
import faker
import random


class Command(BaseCommand):
    help = 'Creates admin user with all privileges and staff rights'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='', help='Username for admin (optional)')
        parser.add_argument('--email', type=str, default='', help='Email for admin (optional)')
        parser.add_argument('--password', type=str, default='', help='Password for admin (optional)')

    def handle(self, *args, **options):
        fake = faker.Faker()
        
        # Check if we should use provided values or generate random ones
        username = options['username'] or f"admin{random.randint(1000, 9999)}"
        email = options['email'] or f"{username}@example.com"
        password = options['password'] or 'AdminSecure123!'
        
        # Check if username exists, if so, add a random number
        if UserProfile.objects.filter(username=username).exists():
            username = f"{username}{random.randint(1000, 9999)}"
            self.stdout.write(self.style.WARNING(f'Username already exists, using {username} instead'))
        
        try:
            # Important: We need to disable the post_save signal temporarily
            # Since we can't easily access the signal handlers directly, we'll use create_user
            # which handles the relationships correctly
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Using create_user instead of create to ensure password is hashed
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin',  # Setting role as admin
                phone_number=fake.phone_number()[:15],
                is_staff=True,
                is_superuser=True  # Gives all privileges
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'Username: {user.username}\n'
                f'Email: {user.email}\n'
                f'Password: {password}\n'
                f'Full Name: {user.get_full_name()}\n'
                f'Role: {user.role}\n'
                f'Staff Status: {user.is_staff}\n'
                f'Superuser Status: {user.is_superuser}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create admin user: {str(e)}'))
            # If the error is due to the signal
            if "UNIQUE constraint failed" in str(e):
                self.stdout.write(self.style.ERROR(
                    'Error occurred due to the post_save signal in backed/models.py. '
                    'Please check the create_user_profile function in your models.py '
                    'that may be creating duplicate users.'
                ))
                self.stdout.write(self.style.WARNING(
                    'You may need to modify the signal handler to check if the user already exists:\n'
                    '@receiver(post_save, sender=UserProfile)\n'
                    'def create_user_profile(sender, instance, created, **kwargs):\n'
                    '    """Create a UserProfile automatically when a UserProfile is created."""\n'
                    '    if created and not UserProfile.objects.filter(username=instance.username).exclude(pk=instance.pk).exists():\n'
                    '        UserProfile.objects.create(username=instance.username, role="client")'
                ))