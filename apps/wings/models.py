from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Wing(models.Model):
    class WingType(models.TextChoices):
        LANGUAGE = 'LANGUAGE', 'Language Wing'
        OPERATIONAL = 'OPERATIONAL', 'Operational Team'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    wing_type = models.CharField(max_length=20, choices=WingType.choices, default=WingType.LANGUAGE)
    language_code = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    coordinator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_wings',
    )
    is_public = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wings:detail', kwargs={'slug': self.slug})


class WingMembership(models.Model):
    class RoleInWing(models.TextChoices):
        MEMBER = 'MEMBER', 'Member'
        COORDINATOR = 'COORDINATOR', 'Coordinator'

    wing = models.ForeignKey(Wing, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='wing_memberships')
    role_in_wing = models.CharField(max_length=20, choices=RoleInWing.choices, default=RoleInWing.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wing', 'user')
        ordering = ['wing', 'user__username']

    def __str__(self):
        return f'{self.user.username} — {self.wing.name}'
