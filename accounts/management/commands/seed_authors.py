from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User, Author

class Command(BaseCommand):
    help = "Creates Author profiles for all users without one."

    def handle(self, *args, **options):
        fake = Faker()
        authors = [
            Author(user=user, description=fake.text(max_nb_chars=200))
            for user in User.objects.all() if not hasattr(user, "author_profile")
        ]
        Author.objects.bulk_create(authors)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(authors)} authors"))
