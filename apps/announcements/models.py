from django.db import models


class AnnouncementQuerySet(models.QuerySet):
    def public(self):
        return self.filter(audience=Announcement.Audience.PUBLIC, is_published=True)

    def for_user(self, user):
        if not user.is_authenticated:
            return self.public()
        qs = self.filter(is_published=True)
        from apps.accounts.models import ClubMembership
        role = getattr(getattr(user, 'club_membership', None), 'role', None)
        audience_filter = models.Q(audience=Announcement.Audience.PUBLIC)
        if role:
            audience_filter |= models.Q(audience=Announcement.Audience.MEMBERS)
        if role == ClubMembership.Role.LEAD:
            audience_filter |= models.Q(audience=Announcement.Audience.CORE_TEAM)
            audience_filter |= models.Q(audience=Announcement.Audience.LEADS)
        wing_ids = user.wing_memberships.values_list('wing_id', flat=True)
        if wing_ids:
            audience_filter |= models.Q(audience=Announcement.Audience.WING, wing_id__in=wing_ids)
        return qs.filter(audience_filter).distinct()


class Announcement(models.Model):
    class Audience(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        MEMBERS = 'MEMBERS', 'All Members'
        CORE_TEAM = 'CORE_TEAM', 'Core Team & Leads'
        LEADS = 'LEADS', 'Leads Only'
        WING = 'WING', 'Specific Wing'

    title = models.CharField(max_length=255)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.MEMBERS)
    wing = models.ForeignKey('wings.Wing', on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    is_pinned = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='announcements')
    published_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ['-is_pinned', '-published_at']

    def __str__(self):
        return self.title
