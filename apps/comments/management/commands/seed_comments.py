from django.core.management.base import BaseCommand
from faker import Faker
import random

from apps.comments.models import Comment
from apps.accounts.models import User
from apps.news.models import News

fake = Faker()


class Command(BaseCommand):
    help = "Seed comments"

    def handle(self, *args, **options):
        users = list(User.objects.all())
        news_list = list(News.objects.all())

        if not users or not news_list:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ No users or news found. "
                    "Run seed_users and seed_news first."
                )
            )
            return

        if Comment.objects.exists():
            self.stdout.write("⚠️ Comments already exist. Skipping.")
            return

        for _ in range(30):
            Comment.objects.create(
                user=random.choice(users),
                news=random.choice(news_list),
                text=fake.text(max_nb_chars=180),
            )

        self.stdout.write(self.style.SUCCESS("✅ Created 30 comments"))