import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Функции для генерации путей загрузки
def user_directory_path(folder_name):
    return lambda instance, filename : f'user_{instance.user.id}/{folder_name}/{uuid.uuid4()}/{filename}'

def presentation_path(instance, filename):
    return f'user_{instance.user.id}/{"presentation"}/{uuid.uuid4()}/{filename}'

def cover_path(instance, filename):
    return f'user_{instance.user.id}/{"cover"}/{uuid.uuid4()}/{filename}'

class Contest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    regulations = models.FileField(upload_to='regulations/')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.title
    
    def get_user_application(self, user):
        try:
            return Application.objects.get(user=user, contest=self)
        except Application.DoesNotExist:
            return None

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey('Contest', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contest')

    def __str__(self):
        return f"{self.user} - {self.contest}"
        
    def is_reviewed(self):
        """Проверяет, есть ли оценки для заявки"""
        return self.reviews.exists()

class ApplicationAnswer(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='answers')
    field = models.ForeignKey('ApplicationField', on_delete=models.CASCADE)
    value = models.TextField()  # Храним текстовое представление, для файлов можно хранить путь

    def __str__(self):
        return f"{self.field.label}: {self.value}"

class ApplicationField(models.Model):
    contest = models.ForeignKey('Contest', on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)  # Внутреннее имя
    label = models.CharField(max_length=200)  # Название, отображаемое пользователю
    field_type = models.CharField(max_length=20, choices=[  # Типы полей
        ('text', 'Текст'),
        ('email', 'Email'),
        ('number', 'Число'),
        ('file', 'Файл'),
        ('image', 'Изображение'),
        ('choice', 'Выбор из списка'),
    ])
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.label} ({self.contest.title})"

class FieldChoice(models.Model):
    field = models.ForeignKey(ApplicationField, on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

class Review(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    innovation = models.IntegerField(verbose_name='Инновационность')
    feasibility = models.IntegerField(verbose_name='Реализуемость')
    impact = models.IntegerField(verbose_name='Влияние')
    presentation_quality = models.IntegerField(verbose_name='Качество презентации')
    total_score = models.IntegerField(verbose_name='Общий балл')
    comment = models.TextField(verbose_name='Комментарий', blank=True)

    def __str__(self):
        return f"Оценка заявки {self.application.id} от {self.reviewer.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class ApplicationProxy(Application):
    class Meta:
        proxy = True
        verbose_name = "Рейтинг заявок"
        verbose_name_plural = "Рейтинг заявок"
