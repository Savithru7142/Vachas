from django.conf import settings
from django.urls import resolve


def site_context(request):
    return {
        'SITE_NAME': settings.VACHAS_SITE_NAME,
        'SITE_TAGLINE': settings.VACHAS_TAGLINE,
    }


def _is_active(request, url_name):
    try:
        match = resolve(request.path)
        namespace, name = url_name.split(':')
        return match.namespace == namespace and match.url_name == name
    except Exception:
        return False


def lead_nav(request):
    ns = 'lead'
    items = [
        ('dashboard', 'Dashboard'),
        ('members', 'Members'),
        ('publications', 'Publications'),
        ('announcements', 'Announcements'),
        ('events', 'Events'),
        ('gallery', 'Gallery'),
        ('contact', 'Contact Messages'),
        ('profile', 'Profile'),
    ]
    return {
        'lead_nav': [
            {'url': f'{ns}:{name}', 'label': label, 'active': _is_active(request, f'{ns}:{name}')}
            for name, label in items
        ]
    }


def member_nav(request):
    ns = 'member'
    items = [
        ('dashboard', 'Dashboard'),
        ('events', 'Events'),
        ('announcements', 'Announcements'),
        ('gallery', 'Gallery'),
        ('publications', 'Publications'),
        ('submissions', 'Submissions'),
        ('tasks', 'Tasks'),
        ('resources', 'Resources'),
        ('profile', 'Profile'),
    ]
    return {
        'member_nav': [
            {'url': f'{ns}:{name}', 'label': label, 'active': _is_active(request, f'{ns}:{name}')}
            for name, label in items
        ]
    }
