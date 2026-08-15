from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with separate system-level developer access."""

    is_developer = models.BooleanField(
        default=False,
        help_text='System-level developer access. Separate from club hierarchy.',
    )

    class Meta:
        ordering = ['username']

    @property
    def display_name(self):
        if hasattr(self, 'profile') and self.profile.display_name:
            return self.profile.display_name
        return self.get_full_name() or self.username

    @property
    def club_role(self):
        if self.is_staff or self.is_superuser:
            return ClubMembership.Role.LEAD
        if hasattr(self, 'club_membership') and self.club_membership.is_active:
            return self.club_membership.role
        return None

    @property
    def is_club_member(self):
        return self.club_role is not None

    @property
    def is_member(self):
        return self.club_role == ClubMembership.Role.MEMBER

    @property
    def is_core_team(self):
        return False

    @property
    def is_lead(self):
        return self.is_staff or self.is_superuser or self.club_role == ClubMembership.Role.LEAD

    @property
    def is_core_or_above(self):
        return self.is_lead

    @property
    def is_lead_or_above(self):
        return self.club_role == ClubMembership.Role.LEAD


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    pen_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_name', 'user__username']

    def __str__(self):
        return self.display_name or self.user.username


class ClubMembership(models.Model):
    class Role(models.TextChoices):
        MEMBER = 'MEMBER', 'Member'
        LEAD = 'LEAD', 'Club Lead'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='club_membership')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    appointed_at = models.DateTimeField(auto_now_add=True)
    appointed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_made',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['role', 'user__username']
        verbose_name = 'Club membership'
        verbose_name_plural = 'Club memberships'

    def __str__(self):
        return f'{self.user.username} — {self.get_role_display()}'


class AuditLog(models.Model):
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions',
    )
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit log'
        verbose_name_plural = 'Audit logs'

    def __str__(self):
        return f'{self.action} at {self.created_at}'
