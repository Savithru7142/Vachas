from django.db import models


class GalleryItem(models.Model):
    title = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_items')
    wing = models.ForeignKey('wings.Wing', on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_items')
    is_public = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='gallery_uploads')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Gallery item'
        verbose_name_plural = 'Gallery items'

    def __str__(self):
        return self.title or f'Gallery item {self.pk}'
