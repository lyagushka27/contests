from django.db import models
from django.contrib.auth.models import User

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
    presentation = models.FileField(upload_to='presentations/')
    cover = models.ImageField(upload_to='covers/')
    created_at = models.DateTimeField(auto_now_add=True)
