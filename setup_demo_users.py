import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django

django.setup()

from django.contrib.auth import authenticate, get_user_model

from apps.accounts.models import ClubMembership
from apps.accounts.permissions import get_dashboard_url

User = get_user_model()

users = [
    ('admin', 'adminpass123', 'admin@example.com', True, True, None),
    ('lead', 'leadpass123', 'lead@example.com', False, False, ClubMembership.Role.LEAD),
    ('member', 'memberpass123', 'member@example.com', False, False, ClubMembership.Role.MEMBER),
]

for username, password, email, is_staff, is_superuser, role in users:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
            'is_active': True,
        },
    )
    user.set_password(password)
    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.is_active = True
    user.save()

    if role is not None:
        ClubMembership.objects.update_or_create(
            user=user,
            defaults={
                'role': role,
                'is_active': True,
            },
        )

    auth_user = authenticate(username=username, password=password)
    print(
        f"{username}: created={created}, auth={auth_user is not None}, "
        f"staff={user.is_staff}, superuser={user.is_superuser}, "
        f"role={getattr(user.club_membership, 'role', 'NO_ROLE') if hasattr(user, 'club_membership') else 'NO_ROLE'}, "
        f"redirect={get_dashboard_url(user)}"
    )
