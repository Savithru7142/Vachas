from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from apps.accounts.permissions import LeadRequiredMixin, log_audit

from .forms import EventForm, EventRegistrationForm
from .models import Event, EventRegistration


class EventListView(ListView):
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        return Event.objects.filter(
            is_public=True,
            status__in=[
                Event.Status.PUBLISHED,
                Event.Status.REGISTRATION_OPEN,
                Event.Status.REGISTRATION_CLOSED,
            ],
        ).select_related('wing', 'organizer')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Event.objects.filter(is_public=True).exclude(status=Event.Status.DRAFT)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            ctx['already_registered'] = EventRegistration.objects.filter(
                event=self.object, user=user, status=EventRegistration.Status.CONFIRMED
            ).exists()
        return ctx


def register_for_event(request, slug):
    event = get_object_or_404(
        Event,
        slug=slug,
        is_public=True,
        status=Event.Status.REGISTRATION_OPEN,
    )
    if event.registration_deadline and timezone.now() > event.registration_deadline:
        messages.error(request, 'Registration deadline has passed.')
        return redirect('events:detail', slug=slug)

    if event.capacity and event.registration_count >= event.capacity:
        messages.error(request, 'This event is at full capacity.')
        return redirect('events:detail', slug=slug)

    if request.user.is_authenticated:
        reg, created = EventRegistration.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'status': EventRegistration.Status.CONFIRMED},
        )
        if created:
            log_audit(request, 'event_registration', 'Event', event.pk)
            messages.success(request, f'You are registered for {event.title}.')
        else:
            messages.info(request, 'You are already registered for this event.')
        return redirect('events:detail', slug=slug)

    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.event = event
            reg.save()
            log_audit(request, 'event_registration_guest', 'Event', event.pk)
            messages.success(request, f'Registration confirmed for {event.title}.')
            return redirect('events:detail', slug=slug)
    else:
        form = EventRegistrationForm()

    return render(request, 'events/register.html', {'event': event, 'form': form})


class LeadEventListView(LeadRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/lead/events.html'
    context_object_name = 'events'


class LeadEventCreateView(LeadRequiredMixin, ListView):
    template_name = 'dashboard/lead/event_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': EventForm(), 'title': 'Create Event'})

    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('lead:events')
        return render(request, self.template_name, {'form': form, 'title': 'Create Event'})


class LeadEventEditView(LeadRequiredMixin, ListView):
    template_name = 'dashboard/lead/event_form.html'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        return render(request, self.template_name, {'form': EventForm(instance=event), 'title': 'Edit Event', 'event': event})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('lead:events')
        return render(request, self.template_name, {'form': form, 'title': 'Edit Event', 'event': event})


class LeadEventRegistrationsView(LeadRequiredMixin, ListView):
    template_name = 'dashboard/lead/event_registrations.html'
    context_object_name = 'registrations'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        registrations = EventRegistration.objects.filter(event=event).order_by('-registered_at')
        return render(
            request,
            self.template_name,
            {
                'event': event,
                'registrations': registrations,
                'registration_count': registrations.filter(status=EventRegistration.Status.CONFIRMED).count(),
            },
        )


# Legacy names kept for any remaining imports
CoreEventListView = LeadEventListView
CoreEventCreateView = LeadEventCreateView
CoreEventEditView = LeadEventEditView
