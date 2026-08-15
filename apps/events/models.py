from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        REGISTRATION_OPEN = 'REGISTRATION_OPEN', 'Registration Open'
        REGISTRATION_CLOSED = 'REGISTRATION_CLOSED', 'Registration Closed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
    )
    wing = models.ForeignKey('wings.Wing', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    poster = models.ImageField(upload_to='events/posters/', blank=True, null=True)
    rules = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:250]
            slug = base
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'slug': self.slug})

    @property
    def is_registration_open(self):
        return self.status == self.Status.REGISTRATION_OPEN

    @property
    def registration_count(self):
        return self.registrations.filter(status=EventRegistration.Status.CONFIRMED).count()


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        WAITLIST = 'WAITLIST', 'Waitlist'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True, related_name='event_registrations')
    guest_name = models.CharField(max_length=150, blank=True)
    guest_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registered_at']
        unique_together = ('event', 'user')

    def __str__(self):
        name = self.user.display_name if self.user else self.guest_name
        return f'{name} — {self.event.title}'

    @property
    def display_name(self):
        if self.user:
            return self.user.display_name
        return self.guest_name
