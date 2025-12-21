from django.core.management.base import BaseCommand
from faker import Faker
from apps.accounts.models import User, Author

fake = Faker()


class Command(BaseCommand):
    help = "Create author profiles for users"

    def handle(self, *args, **options):
        users_without_author = User.objects.filter(author_profile__isnull=True)

        if not users_without_author.exists():
            self.stdout.write("⚠️ All users already have author profiles.")
            return

        count = 0
        for user in users_without_author:
            Author.objects.create(
                user=user,
                description=fake.text(max_nb_chars=200),
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {count} authors"))