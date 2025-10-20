from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

class Command(BaseCommand):
    help = "Creates 20 fake users."

    def handle(self, *args, **options):
        fake = Faker()
        User = get_user_model()

        users = [
            User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                bio=fake.text(max_nb_chars=120),
            )
            for _ in range(20)
        ]
        User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(users)} users"))
