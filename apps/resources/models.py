import uuid

from django.db import models


class Resource(models.Model):
    class Audience(models.TextChoices):
        MEMBERS = 'MEMBERS', 'All Members'
        CORE_TEAM = 'CORE_TEAM', 'Core Team & Leads'
        LEADS = 'LEADS', 'Leads Only'
        WING = 'WING', 'Specific Wing'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='resources/files/')
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.MEMBERS)
    wing = models.ForeignKey('wings.Wing', on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def user_can_access(self, user):
        from apps.accounts.models import ClubMembership
        if not user.is_authenticated or not user.is_club_member:
            return False
        role = user.club_role
        if self.audience == self.Audience.MEMBERS:
            return True
        if self.audience == self.Audience.CORE_TEAM and role == ClubMembership.Role.LEAD:
            return True
        if self.audience == self.Audience.LEADS and role == ClubMembership.Role.LEAD:
            return True
        if self.audience == self.Audience.WING and self.wing_id:
            return user.wing_memberships.filter(wing_id=self.wing_id).exists()
        return False
