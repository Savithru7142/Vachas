from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ClubMembership, Profile, User
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Seed minimal data for THE VACHAS'

    def handle(self, *args, **options):
        self.stdout.write('Seeding THE VACHAS...')

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@thevachas.org', 'first_name': 'System', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True},
        )
        if not admin_user.check_password('adminpass123'):
            admin_user.set_password('adminpass123')
            admin_user.save()
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        Profile.objects.update_or_create(user=admin_user, defaults={'display_name': 'Site Admin'})
        ClubMembership.objects.update_or_create(
            user=admin_user,
            defaults={'role': ClubMembership.Role.LEAD, 'is_active': True},
        )

        lead, _ = User.objects.get_or_create(
            username='lead',
            defaults={'email': 'lead@thevachas.org', 'first_name': 'Lead', 'last_name': 'User'},
        )
        if not lead.check_password('leadpass123'):
            lead.set_password('leadpass123')
            lead.save()
        Profile.objects.update_or_create(user=lead, defaults={'display_name': 'Club Lead'})
        ClubMembership.objects.update_or_create(
            user=lead,
            defaults={'role': ClubMembership.Role.LEAD, 'is_active': True},
        )

        member, _ = User.objects.get_or_create(
            username='member',
            defaults={'email': 'member@thevachas.org', 'first_name': 'Sample', 'last_name': 'Member'},
        )
        if not member.check_password('memberpass123'):
            member.set_password('memberpass123')
            member.save()
        Profile.objects.update_or_create(user=member, defaults={'display_name': 'Sample Member'})
        ClubMembership.objects.update_or_create(
            user=member,
            defaults={'role': ClubMembership.Role.MEMBER, 'is_active': True},
        )

        Event.objects.get_or_create(
            slug='welcome-meet',
            defaults={
                'title': 'Welcome Meet',
                'description': 'Join us for our literature club welcome session.',
                'date': timezone.now() + timedelta(days=14),
                'venue': 'Club Hall',
                'status': Event.Status.REGISTRATION_OPEN,
                'is_public': True,
                'organizer': lead,
                'created_by': lead,
            },
        )

        self.stdout.write(self.style.SUCCESS('Done. Admin login: admin/adminpass123 | Lead login: lead/leadpass123 | Member login: member/memberpass123'))
