from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid


class User(AbstractUser):
    class Meta:
        db_table = "user"

    def user_directory_path(self, filename):
        return f'user/{self.id}/{str(uuid.uuid4())}.{filename.split(".")[-1]}'

    bio = models.TextField(max_length=200, default="", blank=True, null=True)
    avatar = ProcessedImageField(
        blank=True,
        null=True,
        upload_to=user_directory_path,
        processors=[ResizeToFill(150, 150)],
        options={"quality": 80},
    )

    def getAvatar(self):
        return (
            self.avatar.url
            if self.avatar
            else f"{settings.STATIC_URL}img/avatar.svg"
        )
