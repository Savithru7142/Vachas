import os
import sys
from datetime import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import ClubMembership
from apps.announcements.models import Announcement
from apps.events.models import Event
from apps.publications.models import Publication, PublicationCategory
from apps.wings.models import Wing

User = get_user_model()

# Ensure demo user exists
user, _ = User.objects.get_or_create(
    username='member',
    defaults={
        'email': 'member@example.com',
        'is_active': True,
    }
)
user.set_password('memberpass123')
user.save()

# Ensure club membership
ClubMembership.objects.update_or_create(
    user=user,
    defaults={
        'role': ClubMembership.Role.MEMBER,
        'is_active': True,
    }
)

# 1. Wings
wings_data = [
    ('Telugu', 'telugu', 'Celebrating Telugu language and literature.', 'LANGUAGE', 1),
    ('Hindi', 'hindi', 'Expressions in Hindi, echoes of our roots.', 'LANGUAGE', 2),
    ('English', 'english', 'Ideas that inspire, words that connect.', 'LANGUAGE', 3),
    ('Content Team', 'content-team', 'Crafting thoughts, curating voices.', 'OPERATIONAL', 4),
]

wings = {}
for name, slug, desc, w_type, order in wings_data:
    w, _ = Wing.objects.update_or_create(
        slug=slug,
        defaults={
            'name': name,
            'description': desc,
            'wing_type': w_type,
            'display_order': order,
            'is_public': True,
        }
    )
    wings[slug] = w
    print(f"Wing: {w.name}")

# 2. Categories
cat_poem, _ = PublicationCategory.objects.get_or_create(
    slug='poem',
    defaults={'name': 'Poem'}
)
cat_story, _ = PublicationCategory.objects.get_or_create(
    slug='short-story',
    defaults={'name': 'Short Story'}
)
cat_article, _ = PublicationCategory.objects.get_or_create(
    slug='article',
    defaults={'name': 'Article'}
)

# 3. Featured Publication matching the picture
pub, created = Publication.objects.update_or_create(
    slug='the-silence-between-us',
    defaults={
        'title': 'The Silence Between Us',
        'author': user,
        'pen_name': 'Ananya S.',
        'category': cat_poem,
        'wing': wings.get('english'),
        'status': Publication.Status.PUBLISHED,
        'excerpt': 'Sometimes, silence speaks the loudest. Sometimes, it breaks everything.',
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
    }
)
print(f"Publication: {pub.title} (Created: {created})")

# 4. Upcoming Event matching the picture
event_date = timezone.now().date() + timezone.timedelta(days=14)
event, e_created = Event.objects.update_or_create(
    slug='poetry-slam-25',
    defaults={
        'title': "Poetry Slam'25",
        'description': "Join us for an exhilarating evening of spoken word, original poetry, and rhythm. Express your deepest emotions on stage.",
        'venue': 'Main Auditorium, Campus Center',
        'date': event_date,
        'start_time': time(17, 0),
        'end_time': time(20, 0),
        'status': Event.Status.REGISTRATION_OPEN,
        'is_public': True,
        'capacity': 100,
    }
)
print(f"Event: {event.title} (Created: {e_created})")

# 5. Announcement matching the picture
ann, a_created = Announcement.objects.update_or_create(
    title='Open Mic Registrations Now Open!',
    defaults={
        'body': 'Showcase your talent at our annual Open Mic event. Registrations are now open for poetry, storytelling, and acoustic performances.',
        'audience': Announcement.Audience.PUBLIC,
        'is_published': True,
        'created_by': user,
    }
)
print(f"Announcement: {ann.title} (Created: {a_created})")

print("Demo content successfully seeded!")
