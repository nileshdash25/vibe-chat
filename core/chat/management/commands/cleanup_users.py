from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes inactive guest and registered users'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # 1. GUEST USERS: Delete if inactive for 24 hours
        guest_limit = now - timedelta(hours=24)
        # Guests wo hain jinki email nahi hai
        guests_to_del = User.objects.filter(email='', profile__last_seen__lt=guest_limit)
        g_count = guests_to_del.count()
        guests_to_del.delete()

        # 2. REGISTERED USERS: Delete if no login for 3 months
        member_limit = now - timedelta(days=90)
        # Members wo hain jinki email hai
        members_to_del = User.objects.filter(email__contains='@', last_login__lt=member_limit)
        m_count = members_to_del.count()
        members_to_del.delete()

        self.stdout.write(f"Successfully deleted {g_count} guests and {m_count} members.")