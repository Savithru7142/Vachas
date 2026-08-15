from django.contrib import admin
from django.utils import timezone

from .models import Publication, PublicationCategory


@admin.register(PublicationCategory)
class PublicationCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pen_name', 'wing', 'category', 'status', 'created_at', 'published_at')
    list_filter = ('status', 'wing', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'author__username', 'author__first_name', 'author__last_name', 'pen_name', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_published', 'mark_approved', 'mark_under_review', 'mark_rejected']

    fieldsets = (
        ('Submission Info', {
            'fields': ('title', 'slug', 'author', 'pen_name', 'wing', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'cover_image')
        }),
        ('Review & Status', {
            'fields': ('status', 'review_notes', 'reviewed_by', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.action(description='Mark selected as Published')
    def mark_published(self, request, queryset):
        count = queryset.update(status=Publication.Status.PUBLISHED, published_at=timezone.now(), reviewed_by=request.user)
        self.message_user(request, f'{count} publication(s) marked as Published.')

    @admin.action(description='Mark selected as Approved')
    def mark_approved(self, request, queryset):
        count = queryset.update(status=Publication.Status.APPROVED, reviewed_by=request.user)
        self.message_user(request, f'{count} publication(s) marked as Approved.')

    @admin.action(description='Mark selected as Under Review')
    def mark_under_review(self, request, queryset):
        count = queryset.update(status=Publication.Status.UNDER_REVIEW, reviewed_by=request.user)
        self.message_user(request, f'{count} publication(s) marked as Under Review.')

    @admin.action(description='Mark selected as Rejected')
    def mark_rejected(self, request, queryset):
        count = queryset.update(status=Publication.Status.REJECTED, reviewed_by=request.user)
        self.message_user(request, f'{count} publication(s) marked as Rejected.')
