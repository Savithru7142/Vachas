from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'wing', 'uploaded_by', 'created_at')
    list_filter = ('audience', 'wing')
    readonly_fields = ('uuid',)
