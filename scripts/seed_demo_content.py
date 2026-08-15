import os

import django
from django.contrib.auth import get_user_model
from django.utils import timezone

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.production'
)

django.setup()

from apps.accounts.models import ClubMembership
from apps.announcements.models import Announcement
from apps.publications.models import Publication, PublicationCategory
from apps.wings.models import Wing


User = get_user_model()


# ============================================================
# 1. DEMO MEMBER
# ============================================================

user, _ = User.objects.get_or_create(
    username='member',
    defaults={
        'email': 'member@example.com',
        'is_active': True,
    }
)

user.set_password('memberpass123')
user.save()

ClubMembership.objects.update_or_create(
    user=user,
    defaults={
        'role': ClubMembership.Role.MEMBER,
        'is_active': True,
    }
)


# ============================================================
# 2. WINGS
# ============================================================

wings_data = [
    (
        'Telugu',
        'telugu',
        'Celebrating Telugu language and literature.',
        'LANGUAGE',
        1,
    ),
    (
        'Hindi',
        'hindi',
        'Expressions in Hindi, echoes of our roots.',
        'LANGUAGE',
        2,
    ),
    (
        'English',
        'english',
        'Ideas that inspire, words that connect.',
        'LANGUAGE',
        3,
    ),
    (
        'Content Team',
        'content-team',
        'Crafting thoughts, curating voices.',
        'OPERATIONAL',
        4,
    ),
]

wings = {}

for name, slug, desc, wing_type, order in wings_data:
    wing, _ = Wing.objects.update_or_create(
        slug=slug,
        defaults={
            'name': name,
            'description': desc,
            'wing_type': wing_type,
            'display_order': order,
            'is_public': True,
        },
    )

    wings[slug] = wing
    print(f'Wing: {wing.name}')


# ============================================================
# 3. CONTENT CATEGORIES
# ============================================================

categories = [
    ('Article', 'article'),
    ('Essay', 'essay'),
    ('Poem', 'poem'),
    ('Poetry', 'poetry'),
    ('Short Story', 'short-story'),
]

for name, slug in categories:
    category, _ = PublicationCategory.objects.update_or_create(
        slug=slug,
        defaults={
            'name': name,
        },
    )

    print(f'Category: {category.name}')


# ============================================================
# 4. FEATURED PUBLICATION
# ============================================================

poem_category = PublicationCategory.objects.get(
    slug='poem'
)

pub, created = Publication.objects.update_or_create(
    slug='the-silence-between-us',
    defaults={
        'title': 'The Silence Between Us',
        'author': user,
        'pen_name': 'Ananya S.',
        'category': poem_category,
        'wing': wings.get('english'),
        'status': Publication.Status.PUBLISHED,
        'excerpt': (
            'Sometimes, silence speaks the loudest. '
            'Sometimes, it breaks everything.'
        ),
        'content': '''Sometimes, silence speaks the loudest.
Sometimes, it breaks everything.

In the quiet corners of forgotten afternoons,
words unsaid gather like dust on window panes.
We sat across the wooden table,
watching the tea grow cold,
measuring the distance between our thoughts
in the spaces between each breath.

A pen poised above paper,
waiting for courage to spill into ink.''',
        'published_at': timezone.now(),
    },
)

print(
    f'Publication: {pub.title} '
    f'(Created: {created})'
)


# ============================================================
# 5. ANNOUNCEMENT
# ============================================================

ann, created = Announcement.objects.update_or_create(
    title='Open Mic Registrations Now Open!',
    defaults={
        'body': (
            'Showcase your talent at our annual Open Mic event. '
            'Registrations are now open for poetry, storytelling, '
            'and acoustic performances.'
        ),
        'audience': Announcement.Audience.PUBLIC,
        'is_published': True,
        'created_by': user,
    },
)

print(
    f'Announcement: {ann.title} '
    f'(Created: {created})'
)


print('THE VACHAS demo content successfully seeded!')