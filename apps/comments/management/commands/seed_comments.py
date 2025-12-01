from django.core.management.base import BaseCommand
from faker import Faker
import random
from apps.comments.models import Comment
from apps.accounts.models import User
from apps.news.models import News

class Command(BaseCommand):
    help = "Creates 30 fake comments."

    def handle(self, *args, **options):
        fake = Faker()
        users = list(User.objects.all())
        news_list = list(News.objects.all())

        if not users or not news_list:
            self.stdout.write(self.style.WARNING("⚠️ No users or news found. Run seed_users and seed_news first."))
            return

        comments = [
            Comment(
                news=random.choice(news_list),
                user=random.choice(users),
                text=fake.text(max_nb_chars=180),
            )
            for _ in range(30)
        ]
        Comment.objects.bulk_create(comments)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(comments)} comments"))
