from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView

from apps.accounts.models import ClubMembership, User
from apps.accounts.permissions import CoreRequiredMixin, core_required, log_audit
from apps.accounts.views_users import (
    ManagedUsersListMixin,
    approve_managed_user,
    edit_managed_user,
)
from apps.announcements.forms import AnnouncementForm
from apps.announcements.models import Announcement
from apps.core import views_core  # noqa — self-reference for lead imports
from apps.core.dashboard_utils import dash_redirect
from apps.core.forms import AchievementForm
from apps.core.models import Achievement
from apps.events.models import Event
from apps.gallery.forms import GalleryItemForm
from apps.gallery.models import GalleryItem
from apps.publications.models import Publication
from apps.resources.forms import ResourceForm
from apps.resources.models import Resource
from apps.tasks.forms import TaskForm
from apps.tasks.models import Task


class CoreDashboardView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/home.html'

    def get(self, request):
        users = User.objects.select_related('profile', 'club_membership').order_by('-date_joined')
        return render(request, self.template_name, {
            'pending_reviews': Publication.objects.filter(
                status__in=[Publication.Status.SUBMITTED, Publication.Status.UNDER_REVIEW]
            ).count(),
            'open_tasks': Task.objects.exclude(status=Task.Status.COMPLETED).count(),
            'upcoming_events': Event.objects.exclude(status=Event.Status.DRAFT).count(),
            'recent_announcements': Announcement.objects.all()[:5],
            'pending_members': ClubMembership.objects.filter(is_active=False).count(),
            'users': users,
            'total_users': users.count(),
        })


class CoreMembersView(CoreRequiredMixin, ManagedUsersListMixin, ListView):
    template_name = 'dashboard/core/members.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clear_url'] = reverse('core_team:members')
        return ctx


@core_required
def core_edit_user(request, pk):
    return edit_managed_user(
        request,
        pk,
        members_url='core_team:members',
        dashboard_base='dashboard/core/base.html',
    )


@core_required
def core_approve_member(request, pk):
    return approve_managed_user(request, pk, members_url='core_team:members')


class CoreTasksView(CoreRequiredMixin, ListView):
    model = Task
    template_name = 'dashboard/core/tasks.html'
    context_object_name = 'tasks'


class CoreTaskCreateView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/task_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': TaskForm(), 'title': 'Assign Task'})

    def post(self, request):
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            log_audit(request, 'task_created', 'Task', task.pk)
            messages.success(request, 'Task assigned successfully.')
            return dash_redirect(request, 'tasks')
        return render(request, self.template_name, {'form': form, 'title': 'Assign Task'})


def core_task_edit(request, pk):
    from apps.accounts.permissions import user_can_access_core_dashboard
    if not user_can_access_core_dashboard(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated.')
            return dash_redirect(request, 'tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'dashboard/core/task_form.html', {'form': form, 'title': 'Edit Task'})


class CoreAnnouncementsView(CoreRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/core/announcements.html'
    context_object_name = 'announcements'


class CoreAnnouncementCreateView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/announcement_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': AnnouncementForm(), 'title': 'New Announcement'})

    def post(self, request):
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement published.')
            return dash_redirect(request, 'announcements')
        return render(request, self.template_name, {'form': form, 'title': 'New Announcement'})


class CoreResourcesView(CoreRequiredMixin, ListView):
    model = Resource
    template_name = 'dashboard/core/resources.html'
    context_object_name = 'resources'


class CoreResourceUploadView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/resource_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ResourceForm(), 'title': 'Upload Resource'})

    def post(self, request):
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource uploaded.')
            return dash_redirect(request, 'resources')
        return render(request, self.template_name, {'form': form, 'title': 'Upload Resource'})


class CoreGalleryView(CoreRequiredMixin, ListView):
    model = GalleryItem
    template_name = 'dashboard/core/gallery.html'
    context_object_name = 'items'


class CoreGalleryUploadView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/gallery_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': GalleryItemForm(), 'title': 'Upload Gallery Image'})

    def post(self, request):
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            item.save()
            messages.success(request, 'Gallery image uploaded.')
            return dash_redirect(request, 'gallery')
        return render(request, self.template_name, {'form': form, 'title': 'Upload Gallery Image'})


class CoreAchievementsView(CoreRequiredMixin, ListView):
    model = Achievement
    template_name = 'dashboard/core/achievements.html'
    context_object_name = 'achievements'


class CoreAchievementCreateView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/achievement_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': AchievementForm(), 'title': 'Add Achievement'})

    def post(self, request):
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Achievement added.')
            return dash_redirect(request, 'achievements')
        return render(request, self.template_name, {'form': form, 'title': 'Add Achievement'})


class CoreAnalyticsView(CoreRequiredMixin, ListView):
    template_name = 'dashboard/core/analytics.html'

    def get(self, request):
        return render(request, self.template_name, {
            'member_count': ClubMembership.objects.filter(is_active=True).count(),
            'publication_count': Publication.objects.published().count(),
            'event_count': Event.objects.exclude(status=Event.Status.DRAFT).count(),
            'task_count': Task.objects.count(),
            'gallery_count': GalleryItem.objects.filter(is_public=True).count(),
            'achievement_count': Achievement.objects.filter(is_public=True).count(),
        })
