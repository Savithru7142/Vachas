from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from apps.accounts.models import ClubMembership, User
from apps.accounts.permissions import DeveloperRequiredMixin, developer_required
from apps.accounts.views_users import (
    ManagedUsersListMixin,
    approve_managed_user,
    edit_managed_user,
)
from apps.announcements.models import Announcement
from apps.events.models import Event
from apps.publications.models import Publication
from apps.tasks.models import Task


@developer_required
def developer_dashboard(request):
    users = User.objects.select_related('profile', 'club_membership').order_by('-date_joined')[:10]
    return render(request, 'dashboard/developer/home.html', {
        'total_users': User.objects.count(),
        'general_users': User.objects.filter(club_membership__isnull=True).count(),
        'members': ClubMembership.objects.filter(is_active=True).count(),
        'developers': User.objects.filter(is_developer=True).count(),
        'publications': Publication.objects.count(),
        'events': Event.objects.count(),
        'tasks': Task.objects.count(),
        'announcements': Announcement.objects.count(),
        'users': users,
    })


class DeveloperUsersView(DeveloperRequiredMixin, ManagedUsersListMixin, ListView):
    template_name = 'dashboard/developer/users.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clear_url'] = reverse('developer:users')
        return ctx


@developer_required
def developer_edit_user(request, pk):
    return edit_managed_user(
        request,
        pk,
        members_url='developer:users',
        dashboard_base='dashboard/developer/base.html',
    )


@developer_required
def developer_approve_member(request, pk):
    return approve_managed_user(request, pk, members_url='developer:users')


@developer_required
def developer_audit_logs(request):
    from apps.accounts.models import AuditLog
    logs = AuditLog.objects.select_related('actor')[:100]
    return render(request, 'dashboard/developer/audit_logs.html', {'logs': logs})
