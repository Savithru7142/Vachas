from django.contrib import admin

from .models import Event, EventRegistration


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'status', 'venue', 'is_public')
    list_filter = ('status', 'is_public', 'wing')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EventRegistrationInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'guest_name', 'status', 'registered_at')
    list_filter = ('status', 'event')
