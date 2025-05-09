from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.utils import timezone
from backed.models import UserProfile  # Replace 'your_app' with your actual app name
import faker
import random


class Command(BaseCommand):
    help = 'Creates sample users with different roles including admin users with all privileges'

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, default=10, help='Number of users to create')
        parser.add_argument('--admins', type=int, default=1, help='Number of admin users to create')

    def handle(self, *args, **options):
        fake = faker.Faker()
        total_users = options['total']
        admin_count = options['admins']
        
        if admin_count > total_users:
            self.stdout.write(self.style.ERROR('Admin count cannot be greater than total users'))
            return
            
        # Calculate how many of each role to create
        client_count = (total_users - admin_count) // 2
        delivery_count = total_users - admin_count - client_count
        
        self.stdout.write(self.style.SUCCESS(f'Creating {total_users} users:'))
        self.stdout.write(f'- {admin_count} admin users')
        self.stdout.write(f'- {client_count} client users')
        self.stdout.write(f'- {delivery_count} delivery users')
        
        users_created = 0
        
        # Create admin users first
        for i in range(admin_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{username}@{fake.domain_name()}"
            
            # Check if username exists, if so, add a random number
            if UserProfile.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1, 999)}"
            
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password='Admin123!',  # Strong default password
                first_name=first_name,
                last_name=last_name,
                role='admin',
                phone_number=fake.phone_number()[:15],
                is_staff=True,
                is_superuser=True  # Gives all privileges
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'Created admin user: {user.username} ({user.email}) - Password: Admin123!'
            ))
            users_created += 1
        
        # Create client users
        for i in range(client_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{username}@{fake.domain_name()}"
            
            # Check if username exists, if so, add a random number
            if UserProfile.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1, 999)}"
            
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password='Client123!',  # Strong default password
                first_name=first_name,
                last_name=last_name,
                role='client',
                phone_number=fake.phone_number()[:15]
            )
            
            self.stdout.write(
                f'Created client user: {user.username} ({user.email})'
            )
            users_created += 1
        
        # Create delivery users
        for i in range(delivery_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{username}@{fake.domain_name()}"
            
            # Check if username exists, if so, add a random number
            if UserProfile.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1, 999)}"
            
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password='Delivery123!',  # Strong default password
                first_name=first_name,
                last_name=last_name,
                role='delivery',
                phone_number=fake.phone_number()[:15]
            )
            
            self.stdout.write(
                f'Created delivery user: {user.username} ({user.email})'
            )
            users_created += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {users_created} users'))