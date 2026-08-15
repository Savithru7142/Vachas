import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django

django.setup()

from django.contrib.auth import get_user_model

from apps.accounts.models import ClubMembership

User = get_user_model()

for username, role, is_staff, is_superuser in [
    ('lead', ClubMembership.Role.LEAD, False, False),
    ('member', ClubMembership.Role.MEMBER, False, False),
    ('admin', None, True, True),
]:
    user = User.objects.get(username=username)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()

    if role is None:
        ClubMembership.objects.filter(user=user).delete()
    else:
        ClubMembership.objects.update_or_create(
            user=user,
            defaults={'role': role, 'is_active': True},
        )

    print(
        username,
        'staff=', user.is_staff,
        'superuser=', user.is_superuser,
        'role=', getattr(getattr(user, 'club_membership', None), 'role', 'NO_ROLE')
    )
