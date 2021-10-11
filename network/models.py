from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField(
        "User",
        related_name="followers"
    )


class Post(models.Model):
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_uploader"
    )
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User,
        related_name="post_liked"
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Post uploaded by {self.uploader}"

    def serialize(self):
        return {
            "id": self.id,
            "uploader": self.uploader.username,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.count(),
            "liked_by": [like.username for like in self.likes.all()]
        }
