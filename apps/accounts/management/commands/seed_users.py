from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed users"

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write("⚠️ Users already exist. Skipping.")
            return

        for _ in range(20):
            User.objects.create_user(
                email=fake.unique.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )

        self.stdout.write(self.style.SUCCESS("✅ Created 20 users"))