from django.db import models
from blogs.models import Blog
from django.conf import settings


# Create your models here.
class Comment(models.Model):

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Like(models.Model):

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blog", "user"], name="unique_like_interaction"
            )
        ]
