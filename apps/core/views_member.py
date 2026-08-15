from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.accounts.permissions import MemberRequiredMixin, log_audit
from apps.announcements.models import Announcement
from apps.events.models import Event, EventRegistration
from apps.gallery.models import GalleryItem
from apps.publications.models import Publication
from apps.resources.models import Resource
from apps.tasks.forms import TaskStatusForm
from apps.tasks.models import Task


class MemberDashboardView(MemberRequiredMixin, ListView):
    template_name = 'dashboard/member/home.html'

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {
            'tasks': Task.objects.filter(assigned_to=user).exclude(status=Task.Status.COMPLETED)[:5],
            'submissions': Publication.objects.for_author(user)[:5],
            'events': Event.objects.filter(
                status__in=[Event.Status.REGISTRATION_OPEN, Event.Status.PUBLISHED]
            )[:4],
            'announcements': Announcement.objects.for_user(user)[:5],
        })


class MemberTasksView(MemberRequiredMixin, ListView):
    model = Task
    template_name = 'dashboard/member/tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


def member_task_update(request, pk):
    from apps.accounts.permissions import user_can_access_member_dashboard
    if not user_can_access_member_dashboard(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task status updated.')
            return redirect('member:tasks')
    else:
        form = TaskStatusForm(instance=task)
    return render(request, 'dashboard/member/task_detail.html', {'task': task, 'form': form})


class MemberEventsView(MemberRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/member/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.exclude(status=Event.Status.DRAFT)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['registrations'] = EventRegistration.objects.filter(
            user=self.request.user, status=EventRegistration.Status.CONFIRMED
        ).select_related('event')
        return ctx


class MemberAnnouncementsView(MemberRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/member/announcements.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        return Announcement.objects.for_user(self.request.user)


class MemberResourcesView(MemberRequiredMixin, ListView):
    model = Resource
    template_name = 'dashboard/member/resources.html'
    context_object_name = 'resources'

    def get_queryset(self):
        return [r for r in Resource.objects.all() if r.user_can_access(self.request.user)]


def member_resource_download(request, uuid):
    from apps.accounts.permissions import user_can_access_member_dashboard
    if not user_can_access_member_dashboard(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    resource = get_object_or_404(Resource, uuid=uuid)
    if not resource.user_can_access(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    log_audit(request, 'resource_download', 'Resource', resource.pk)
    from django.http import FileResponse
    return FileResponse(resource.file.open('rb'), as_attachment=True, filename=resource.file.name.split('/')[-1])


class MemberPublicationsView(MemberRequiredMixin, ListView):
    model = Publication
    template_name = 'dashboard/member/publications.html'
    context_object_name = 'publications'

    def get_queryset(self):
        return Publication.objects.published().select_related('author', 'wing')


class MemberGalleryView(MemberRequiredMixin, ListView):
    model = GalleryItem
    template_name = 'dashboard/member/gallery.html'
    context_object_name = 'items'
    paginate_by = 24

    def get_queryset(self):
        return GalleryItem.objects.filter(is_public=True).order_by('-created_at')
