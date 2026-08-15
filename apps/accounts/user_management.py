"""Shared user listing and editing helpers."""

from django.db import models

from apps.accounts.models import ClubMembership, User


def filter_users_queryset(request):
    qs = User.objects.select_related('profile', 'club_membership').order_by('-date_joined')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            models.Q(username__icontains=q)
            | models.Q(first_name__icontains=q)
            | models.Q(last_name__icontains=q)
            | models.Q(email__icontains=q)
            | models.Q(profile__display_name__icontains=q)
        )
    status = request.GET.get('status')
    if status == 'pending':
        qs = qs.filter(club_membership__is_active=False)
    elif status == 'active':
        qs = qs.filter(club_membership__is_active=True)
    elif status == 'none':
        qs = qs.filter(club_membership__isnull=True)
    return qs


def users_list_context(request):
    return {
        'pending_members': ClubMembership.objects.filter(is_active=False).count(),
        'search_query': request.GET.get('q', ''),
        'status_filter': request.GET.get('status', ''),
        'total_users': User.objects.count(),
    }


def can_edit_user(editor, target):
    return editor.is_lead or editor.pk == target.pk


def validate_user_account_save(editor, target, cleaned_data):
    if editor.pk == target.pk:
        if not cleaned_data.get('is_active', True):
            return 'You cannot deactivate your own account.'
        if editor.is_lead and cleaned_data.get('role') != ClubMembership.Role.LEAD:
            return 'You cannot change your own role away from Club Lead.'
    return None
