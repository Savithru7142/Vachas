from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PublicationCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Publication categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PublicationQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Publication.Status.PUBLISHED)

    def for_reviewer(self):
        return self.exclude(status=Publication.Status.DRAFT)

    def for_author(self, user):
        return self.filter(author=user)


class Publication(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PUBLISHED = 'PUBLISHED', 'Published'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='publications')
    pen_name = models.CharField(max_length=150, blank=True)
    wing = models.ForeignKey('wings.Wing', on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    category = models.ForeignKey(PublicationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='publications/covers/', blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_publications',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    objects = PublicationQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:250]
            slug = base
            counter = 1
            while Publication.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300].strip()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('publications:detail', kwargs={'slug': self.slug})

    @property
    def author_display(self):
        return self.pen_name or self.author.display_name

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def is_public(self):
        return self.status == self.Status.PUBLISHED
