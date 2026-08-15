import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django

django.setup()

from django.contrib.auth import get_user_model

from apps.accounts.models import ClubMembership

User = get_user_model()

for username in ['lead', 'admin', 'member']:
    user = User.objects.get(username=username)
    if username == 'lead':
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.save()
        ClubMembership.objects.update_or_create(
            user=user,
            defaults={'role': ClubMembership.Role.LEAD, 'is_active': True},
        )
    elif username == 'member':
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.save()
        ClubMembership.objects.update_or_create(
            user=user,
            defaults={'role': ClubMembership.Role.MEMBER, 'is_active': True},
        )
    else:
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        ClubMembership.objects.filter(user=user).delete()

    try:
        role = user.club_membership.role
    except Exception:
        role = 'NO_ROLE'

    print(
        username,
        'staff=', user.is_staff,
        'superuser=', user.is_superuser,
        'role=', role
    )
