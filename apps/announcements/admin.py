from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'is_pinned', 'is_published', 'published_at')
    list_filter = ('audience', 'is_pinned', 'is_published')
