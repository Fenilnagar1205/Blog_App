from django.db import models

from django.conf import settings


# Create your models here.
class Blog(models.Model):

    title = models.CharField(max_length=200)

    content = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )

    slug = models.SlugField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    published_at = models.DateTimeField(null=True, blank=True)

    featured_image = models.ImageField(upload_to="blog_images/", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
