from django.core.management.base import BaseCommand
from faker import Faker
from apps.news.models import Category

fake = Faker()


class Command(BaseCommand):
    help = "Seed categories"

    def handle(self, *args, **options):
        if Category.objects.exists():
            self.stdout.write("⚠️ Categories already exist. Skipping.")
            return

        for _ in range(10):
            Category.objects.create(
                name=fake.unique.word()
            )

        self.stdout.write(self.style.SUCCESS("✅ Created 10 categories"))