from django.db import models


class Achievement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    year = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-year', 'title']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} — {self.name}'
