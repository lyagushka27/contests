import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Application, Review


def export_users_to_csv(modeladmin, request, queryset):
    """Экспортирует выбранных пользователей в CSV-файл."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=users.csv'

    response.write('\ufeff'.encode('utf-8'))  

    writer = csv.writer(response)
    writer.writerow(['Username', 'First Name', 'Last Name', 'Email'])

    users = queryset.values_list('username', 'first_name', 'last_name', 'email')
    for user in users:
        writer.writerow(user)

    return response

# Устанавливаем краткое описание для действия
export_users_to_csv.short_description = 'Экспортировать пользователей в CSV' # type: ignore

def export_applications_to_csv(modeladmin, request, queryset):
    """Экспортирует выбранные заявки в CSV-файл."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=applications.csv'

    response.write('\ufeff'.encode('utf-8'))  
    writer = csv.writer(response)
    writer.writerow([
        'Startup Name', 'First Name', 'Last Name', 'Middle Name', 'Phone',
        'Email', 'Organization', 'Age', 'Class Number', 'Nomination', 'Description', 'Average Score'
    ])

    for application in queryset:
        avg_score = application.reviews.aggregate(Avg('total_score'))['total_score__avg']
        writer.writerow([
            application.startup_name, application.first_name, application.last_name,
            application.middle_name, application.phone, application.email,
            application.organization, application.age, application.class_number,
            application.nomination, application.startup_description, avg_score
        ])

    return response

export_applications_to_csv.short_description = 'Экспортировать заявки в CSV' # type: ignore

def export_rating_to_csv(modeladmin, request, queryset):
    """Экспортирует рейтинг заявок в CSV-файл."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=rating.csv'

    writer = csv.writer(response)
    writer.writerow(['Startup Name','First Name', 'Last Name', 'Average Score'])

    # Агрегируем данные о среднем балле
    applications = queryset.annotate(average_score=Avg('reviews__total_score'))

    for application in applications:
        writer.writerow([application.startup_name, application.first_name, application.last_name, application.average_score])

    return response

export_rating_to_csv.short_description = 'Экспортировать рейтинг в CSV' # type: ignore

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    verbose_name = "Оценка"
    verbose_name_plural = "Оценки"

class ReviewedFilter(admin.SimpleListFilter):
    title = 'Статус оценки'
    parameter_name = 'reviewed'

    def lookups(self, request, model_admin): # type: ignore
        return (
            ('yes', 'Оцененные'),
            ('no', 'Неоцененные'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(reviews__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(reviews__isnull=True)

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('startup_name', 'user', 'average_score', 'is_reviewed')
    list_filter = (ReviewedFilter,)
    inlines = [ReviewInline]
    actions = [export_applications_to_csv]

    def average_score(self, obj):
        return obj.reviews.aggregate(Avg('total_score'))['total_score__avg']

    def is_reviewed(self, obj):
        return obj.reviews.exists()

    average_score.short_description = 'Средний балл' # type: ignore
    is_reviewed.boolean = True # type: ignore

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(average_score=Avg('reviews__total_score'))

class UserAdmin(admin.ModelAdmin):
    actions = [export_users_to_csv]

class ApplicationProxy(Application):
    class Meta:
        proxy = True
        verbose_name = "Рейтинг заявок"
        verbose_name_plural = "Рейтинг заявок"

class RatingAdmin(admin.ModelAdmin):
    list_display = ('startup_name', 'average_score')
    actions = [export_rating_to_csv]

    def startup_name(self, obj):
        return obj.startup_name

    def average_score(self, obj):
        return obj.average_score
    average_score.admin_order_field = 'average_score'  # type: ignore # Позволяет сортировать в админке

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(average_score=Avg('reviews__total_score')).order_by('-average_score')


# Регистрация моделей в админ-панели
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Review)
admin.site.register(ApplicationProxy, RatingAdmin)