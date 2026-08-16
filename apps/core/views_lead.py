from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from apps.accounts.forms import RegisterForm
from apps.accounts.models import ClubMembership, User
from apps.accounts.permissions import LeadRequiredMixin, lead_required, log_audit
from apps.accounts.views_users import (
    ManagedUsersListMixin,
    approve_managed_user,
    edit_managed_user,
)
from apps.announcements.forms import AnnouncementForm
from apps.announcements.models import Announcement
from apps.core.models import ContactMessage
from apps.events.models import Event
from apps.gallery.forms import GalleryItemForm
from apps.gallery.models import GalleryItem
from apps.publications.models import Publication


class LeadDashboardView(LeadRequiredMixin, ListView):
    template_name = 'dashboard/lead/home.html'

    def get(self, request):
        return render(request, self.template_name, {
            'total_users': User.objects.count(),
            'member_count': ClubMembership.objects.filter(
                role=ClubMembership.Role.MEMBER,
                is_active=True
            ).count(),
            'pending_submissions': Publication.objects.filter(
                status__in=[
                    Publication.Status.SUBMITTED,
                    Publication.Status.UNDER_REVIEW
                ]
            ).count(),
            'recent_submissions': Publication.objects.exclude(
                status=Publication.Status.DRAFT
            ).select_related(
                'author',
                'wing',
                'category'
            ).order_by('-created_at')[:6],
            'upcoming_events': Event.objects.filter(
                is_public=True
            ).count(),
            'gallery_count': GalleryItem.objects.filter(
                is_public=True
            ).count(),
            'unread_contact': ContactMessage.objects.filter(
                is_read=False
            ).count(),
            'users': User.objects.select_related(
                'profile',
                'club_membership'
            ).order_by('-date_joined')[:8],
        })


class LeadMembersView(
    LeadRequiredMixin,
    ManagedUsersListMixin,
    ListView
):
    template_name = 'dashboard/lead/members.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clear_url'] = reverse('lead:members')
        return ctx


@lead_required
def lead_add_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Created {user.display_name} successfully.'
            )
            return redirect('lead:members')
    else:
        form = RegisterForm()

    return render(
        request,
        'dashboard/lead/user_form.html',
        {
            'form': form,
            'title': 'Add User'
        }
    )


@lead_required
def lead_edit_user(request, pk):
    return edit_managed_user(
        request,
        pk,
        members_url='lead:members',
        dashboard_base='dashboard/lead/base.html',
    )


@lead_required
def lead_approve_member(request, pk):
    return approve_managed_user(
        request,
        pk,
        members_url='lead:members'
    )


@lead_required
def lead_delete_user(request, pk):
    if request.method != 'POST':
        return redirect('lead:members')

    user = get_object_or_404(User, pk=pk)

    if user.pk == request.user.pk:
        messages.error(
            request,
            'You cannot delete your own account.'
        )
        return redirect('lead:members')

    user.delete()

    log_audit(
        request,
        'lead_deleted_user',
        'User',
        pk
    )

    messages.success(
        request,
        'User deleted successfully.'
    )

    return redirect('lead:members')


@lead_required
def lead_announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)

        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()

            messages.success(
                request,
                'Announcement created successfully.'
            )

            return redirect('lead:announcements')
    else:
        form = AnnouncementForm()

    return render(
        request,
        'dashboard/lead/announcement_form.html',
        {
            'form': form,
            'title': 'Create Announcement'
        }
    )


@lead_required
def lead_announcement_edit(request, pk):
    announcement = get_object_or_404(
        Announcement,
        pk=pk
    )

    if request.method == 'POST':
        form = AnnouncementForm(
            request.POST,
            instance=announcement
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Announcement updated successfully.'
            )

            return redirect('lead:announcements')
    else:
        form = AnnouncementForm(
            instance=announcement
        )

    return render(
        request,
        'dashboard/lead/announcement_form.html',
        {
            'form': form,
            'title': 'Edit Announcement',
            'announcement': announcement
        }
    )


@lead_required
def lead_announcement_delete(request, pk):
    if request.method != 'POST':
        return redirect('lead:announcements')

    announcement = get_object_or_404(
        Announcement,
        pk=pk
    )

    announcement.delete()

    messages.success(
        request,
        'Announcement deleted successfully.'
    )

    return redirect('lead:announcements')


class LeadAnnouncementsListView(
    LeadRequiredMixin,
    ListView
):
    model = Announcement
    template_name = 'dashboard/lead/announcements.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        return Announcement.objects.order_by('-published_at')


@lead_required
def lead_event_delete(request, pk):
    if request.method != 'POST':
        return redirect('lead:events')

    event = get_object_or_404(
        Event,
        pk=pk
    )

    event.delete()

    messages.success(
        request,
        'Event deleted successfully.'
    )

    return redirect('lead:events')


class LeadCompletedEventsView(
    LeadRequiredMixin,
    ListView
):
    model = Event
    template_name = 'dashboard/lead/events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
            status=Event.Status.COMPLETED
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['completed_events'] = ctx['events']

        ctx['events'] = Event.objects.filter(
            status__in=[
                Event.Status.PUBLISHED,
                Event.Status.REGISTRATION_OPEN,
                Event.Status.REGISTRATION_CLOSED,
                Event.Status.DRAFT,
            ]
        ).order_by('date')

        return ctx


class LeadGalleryView(
    LeadRequiredMixin,
    ListView
):
    model = GalleryItem
    template_name = 'dashboard/lead/gallery.html'
    context_object_name = 'items'


@lead_required
def lead_gallery_edit(request, pk):
    item = get_object_or_404(
        GalleryItem,
        pk=pk
    )

    if request.method == 'POST':
        form = GalleryItemForm(
            request.POST,
            request.FILES,
            instance=item
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Gallery photo updated.'
            )

            return redirect('lead:gallery')
    else:
        form = GalleryItemForm(
            instance=item
        )

    return render(
        request,
        'dashboard/lead/gallery_form.html',
        {
            'form': form,
            'title': 'Edit Photo',
            'item': item
        }
    )


# ============================================================
# DELETE GALLERY PHOTO
# ============================================================

@lead_required
def lead_gallery_delete(request, pk):
    if request.method != 'POST':
        return redirect('lead:gallery')

    item = get_object_or_404(
        GalleryItem,
        pk=pk
    )

    # Delete the image from Cloudinary/storage
    # before deleting the database record.
    if item.image:
        item.image.delete(save=False)

    item.delete()

    messages.success(
        request,
        'Gallery photo deleted successfully.'
    )

    return redirect('lead:gallery')


class LeadGalleryUploadView(
    LeadRequiredMixin,
    ListView
):
    template_name = 'dashboard/lead/gallery_form.html'

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                'form': GalleryItemForm(),
                'title': 'Upload Photo'
            }
        )

    def post(self, request):
        form = GalleryItemForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            item = form.save(
                commit=False
            )

            item.uploaded_by = request.user
            item.save()

            messages.success(
                request,
                'Gallery photo uploaded.'
            )

            return redirect('lead:gallery')

        return render(
            request,
            self.template_name,
            {
                'form': form,
                'title': 'Upload Photo'
            }
        )


class LeadContactMessagesView(
    LeadRequiredMixin,
    ListView
):
    model = ContactMessage
    template_name = 'dashboard/lead/contact.html'
    context_object_name = 'messages_list'

    def get_queryset(self):
        return ContactMessage.objects.order_by(
            '-created_at'
        )