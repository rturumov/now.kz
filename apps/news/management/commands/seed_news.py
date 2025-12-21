from django.core.management.base import BaseCommand
from faker import Faker
import random

from apps.news.models import News, Category
from apps.accounts.models import Author

fake = Faker()


class Command(BaseCommand):
    help = "Seed news"

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        authors = list(Author.objects.all())

        if not categories or not authors:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ No categories or authors found. "
                    "Run seed_categories and seed_authors first."
                )
            )
            return

        if News.objects.exists():
            self.stdout.write("⚠️ News already exist. Skipping.")
            return

        for _ in range(20):
            News.objects.create(
                title=fake.sentence(),
                content=fake.text(max_nb_chars=600),
                category=random.choice(categories),
                author=random.choice(authors),
                is_published=True,
            )

        self.stdout.write(self.style.SUCCESS("✅ Created 20 news articles"))