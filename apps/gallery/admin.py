from django.contrib import admin

from .models import GalleryItem


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public', 'wing', 'display_order', 'created_at')
    list_filter = ('is_public', 'wing')
