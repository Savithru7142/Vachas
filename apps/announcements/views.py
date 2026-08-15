from django.views.generic import ListView

from .models import Announcement


class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        return Announcement.objects.public()
