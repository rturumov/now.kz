from django.core.management.base import BaseCommand
from faker import Faker
from contacts.models import ContactMessage

class Command(BaseCommand):
    help = "Creates 15 fake contact messages."

    def handle(self, *args, **options):
        fake = Faker()
        messages = [
            ContactMessage(
                name=fake.name(),
                email=fake.unique.email(),
                subject=fake.sentence(),
                message=fake.text(max_nb_chars=300),
            )
            for _ in range(15)
        ]
        ContactMessage.objects.bulk_create(messages)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(messages)} contact messages"))
