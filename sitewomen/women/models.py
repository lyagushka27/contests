import uuid
from django.db import models
from django.contrib.auth.models import User

def user_directory_path(folder_name):
    return lambda instance, filename : f'user_{instance.user.id}/{folder_name}/{uuid.uuid4()}/{filename}'

def presentation_path(instance, filename):
    return f'user_{instance.user.id}/{"presentation"}/{uuid.uuid4()}/{filename}'

def cover_path(instance, filename):
     return f'user_{instance.user.id}/{"cover"}/{uuid.uuid4()}/{filename}'

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
    presentation = models.FileField(upload_to=presentation_path)
    cover = models.ImageField(upload_to=cover_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_score(self):
        return self.reviews.aggregate(models.Avg('total_score'))['total_score__avg']

    def is_reviewed(self):
        return self.reviews.exists()
    
class Review(models.Model):
    application = models.ForeignKey(Application, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    innovation = models.IntegerField()
    feasibility = models.IntegerField()
    impact = models.IntegerField()
    presentation_quality = models.IntegerField()
    total_score = models.IntegerField()
    comment = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_score = self.innovation + self.feasibility + self.impact + self.presentation_quality
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
