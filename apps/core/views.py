from django.shortcuts import render

from apps.core.forms import ContactForm
from apps.events.models import Event
from apps.gallery.models import GalleryItem
from apps.publications.models import Publication
from apps.wings.models import Wing


def home(request):
    return render(request, 'core/home.html', {
        'upcoming_events': Event.objects.filter(
            is_public=True,
            status__in=[Event.Status.PUBLISHED, Event.Status.REGISTRATION_OPEN],
        )[:3],
        'gallery_items': GalleryItem.objects.filter(is_public=True)[:6],
        'wings': Wing.objects.all()[:4],
        'featured_publications': Publication.objects.published()[:2],
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Thank you. Your message has been received.')
            return render(request, 'core/contact.html', {'form': ContactForm(), 'sent': True})
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def team(request):
    from apps.accounts.models import ClubMembership
    leads = ClubMembership.objects.filter(
        role=ClubMembership.Role.LEAD, is_active=True
    ).select_related('user', 'user__profile')
    members = ClubMembership.objects.filter(
        role=ClubMembership.Role.MEMBER, is_active=True
    ).select_related('user', 'user__profile')
    return render(request, 'core/team.html', {
        'leads': leads,
        'members': members,
    })


def robots_txt(request):
    from django.http import HttpResponse
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /lead/',
        'Disallow: /admin/',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
