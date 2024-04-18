from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


