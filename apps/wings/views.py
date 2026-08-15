from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from apps.wings.models import Wing


class WingListView(ListView):
    model = Wing
    template_name = 'wings/list.html'
    context_object_name = 'wings'

    def get_queryset(self):
        return Wing.objects.filter(is_public=True)


def wing_detail(request, slug):
    wing = get_object_or_404(Wing, slug=slug, is_public=True)
    publications = wing.publications.filter(status='PUBLISHED')[:6]
    events = wing.events.filter(status__in=['PUBLISHED', 'REGISTRATION_OPEN'])[:4]
    return render(request, 'wings/detail.html', {
        'wing': wing,
        'publications': publications,
        'events': events,
    })
