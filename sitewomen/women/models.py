import uuid
from django.db import models
from django.contrib.auth.models import User


def user_directory_path(folder_name):
    return lambda instance, filename : f'user_{instance.user.id}/{folder_name}/{uuid.uuid4()}/{filename}'


class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    organization = models.CharField(max_length=200)
    age = models.IntegerField()
    class_number = models.CharField(max_length=10)
    nomination = models.CharField(max_length=100)
    startup_name = models.CharField(max_length=200)
    startup_description = models.TextField()
    presentation = models.FileField(upload_to=user_directory_path('presentation'))
    cover = models.ImageField(upload_to=user_directory_path('cover'))
    created_at = models.DateTimeField(auto_now_add=True)
