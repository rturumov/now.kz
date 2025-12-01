from django.core.management.base import BaseCommand
from faker import Faker
import random
from apps.news.models import News, Category
from apps.accounts.models import Author

class Command(BaseCommand):
    help = "Creates 20 fake news articles."

    def handle(self, *args, **options):
        fake = Faker()
        categories = list(Category.objects.all())
        authors = list(Author.objects.all())

        if not categories or not authors:
            self.stdout.write(self.style.WARNING("⚠️ No categories or authors found. Run seed_categories and seed_authors first."))
            return

        news_list = [
            News(
                title=fake.sentence(),
                slug=fake.unique.slug(),
                content=fake.text(max_nb_chars=600),
                category=random.choice(categories),
                author=random.choice(authors),
                is_published=True,
            )
            for _ in range(20)
        ]
        News.objects.bulk_create(news_list)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(news_list)} news articles"))
