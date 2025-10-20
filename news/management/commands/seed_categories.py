from django.core.management.base import BaseCommand
from faker import Faker
from news.models import Category

class Command(BaseCommand):
    help = "Creates 20 fake categories."

    def handle(self, *args, **options):
        fake = Faker()
        categories = [
            Category(name=fake.unique.word(), slug=fake.unique.slug())
            for _ in range(10)
        ]
        Category.objects.bulk_create(categories)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(categories)} categories"))
