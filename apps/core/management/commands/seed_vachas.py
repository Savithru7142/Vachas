
from django.core.management.base import BaseCommand

from apps.accounts.models import ClubMembership, Profile, User
from apps.publications.models import PublicationCategory
from apps.wings.models import Wing


class Command(BaseCommand):
    help = 'Seed complete demo data for THE VACHAS'

    def handle(self, *args, **options):

        self.stdout.write('Seeding THE VACHAS...')

        # ============================================================
        # 1. USERS
        # ============================================================

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@thevachas.org',
                'first_name': 'System',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            },
        )

        if not admin_user.check_password('adminpass123'):
            admin_user.set_password('adminpass123')

        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        Profile.objects.update_or_create(
            user=admin_user,
            defaults={'display_name': 'Site Admin'},
        )

        ClubMembership.objects.update_or_create(
            user=admin_user,
            defaults={
                'role': ClubMembership.Role.LEAD,
                'is_active': True,
            },
        )

        # ------------------------------------------------------------

        lead, _ = User.objects.get_or_create(
            username='lead',
            defaults={
                'email': 'lead@thevachas.org',
                'first_name': 'Lead',
                'last_name': 'User',
            },
        )

        if not lead.check_password('leadpass123'):
            lead.set_password('leadpass123')
            lead.save()

        Profile.objects.update_or_create(
            user=lead,
            defaults={'display_name': 'Club Lead'},
        )

        ClubMembership.objects.update_or_create(
            user=lead,
            defaults={
                'role': ClubMembership.Role.LEAD,
                'is_active': True,
            },
        )

        # ------------------------------------------------------------

        member, _ = User.objects.get_or_create(
            username='member',
            defaults={
                'email': 'member@thevachas.org',
                'first_name': 'Sample',
                'last_name': 'Member',
            },
        )

        if not member.check_password('memberpass123'):
            member.set_password('memberpass123')
            member.save()

        Profile.objects.update_or_create(
            user=member,
            defaults={'display_name': 'Sample Member'},
        )

        ClubMembership.objects.update_or_create(
            user=member,
            defaults={
                'role': ClubMembership.Role.MEMBER,
                'is_active': True,
            },
        )

        self.stdout.write('Users created.')

        # ============================================================
        # 2. WINGS
        # ============================================================

        wings_data = [
            (
                'Telugu',
                'telugu',
                'Celebrating Telugu language and literature.',
                Wing.WingType.LANGUAGE,
                'te',
                1,
            ),
            (
                'Hindi',
                'hindi',
                'Expressions in Hindi, echoes of our roots.',
                Wing.WingType.LANGUAGE,
                'hi',
                2,
            ),
            (
                'English',
                'english',
                'Ideas that inspire, words that connect.',
                Wing.WingType.LANGUAGE,
                'en',
                3,
            ),
            (
                'Content Team',
                'content-team',
                'Crafting thoughts, curating voices.',
                Wing.WingType.OPERATIONAL,
                '',
                4,
            ),
        ]

        wings = {}

        for (
            name,
            slug,
            description,
            wing_type,
            language_code,
            display_order,
        ) in wings_data:

            wing, _ = Wing.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'wing_type': wing_type,
                    'language_code': language_code,
                    'is_public': True,
                    'display_order': display_order,
                },
            )

            wings[slug] = wing

            self.stdout.write(
                self.style.SUCCESS(f'Wing: {wing.name}')
            )

        # ============================================================
        # 3. PUBLICATION CATEGORIES
        # ============================================================

        categories_data = [
            ('Article', 'article'),
            ('Essay', 'essay'),
            ('Poem', 'poem'),
            ('Poetry', 'poetry'),
            ('Short Story', 'short-story'),
        ]

        categories = {}

        for name, slug in categories_data:

            category, _ = PublicationCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                },
            )

            categories[slug] = category

            self.stdout.write(
                self.style.SUCCESS(
                    f'Category: {category.name}'
                )
            )

        # ============================================================
        # DONE
        # ============================================================

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                'THE VACHAS demo content successfully seeded!'
            )
        )

        self.stdout.write('')
        self.stdout.write(
            'Admin: admin / adminpass123'
        )
        self.stdout.write(
            'Lead: lead / leadpass123'
        )
        self.stdout.write(
            'Member: member / memberpass123'
        )