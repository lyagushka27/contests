from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import csv
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.utils.html import format_html
from .models import Application, Contest, Review, ApplicationField, ApplicationAnswer, ApplicationProxy
from django.urls import path
from django.shortcuts import redirect
from .generations_word import generate_contest_report


def export_to_csv(modeladmin, request, queryset, fields, filename):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response.write('\ufeff'.encode('utf-8'))
    
    writer = csv.writer(response)
    writer.writerow(fields)
    
    for obj in queryset:
        row = []
        for field in fields:
            if hasattr(obj, field):
                value = getattr(obj, field)
                if callable(value):
                    value = value()
                row.append(str(value))
        writer.writerow(row)
    
    return response

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

class ApplicationFieldInline(admin.TabularInline):
    model = ApplicationField
    extra = 1

class ApplicationAnswerInline(admin.TabularInline):
    model = ApplicationAnswer
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

class ReviewedFilter(admin.SimpleListFilter):
    title = 'Оценено'
    parameter_name = 'reviewed'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(reviews__isnull=False)
        if self.value() == 'no':
            return queryset.filter(reviews__isnull=True)

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'applications_count', 'download_report')
    search_fields = ('title', 'description')
    inlines = [ApplicationFieldInline]
    
    def applications_count(self, obj):
        return obj.application_set.count()
    applications_count.short_description = 'Количество участников'
    
    actions = ['export_contests_to_csv']
    
    def export_contests_to_csv(self, request, queryset):
        fields = ['Название', 'Дата начала', 'Дата окончания', 'Количество участников']
        return export_to_csv(self, request, queryset, fields, 'contests.csv')
    export_contests_to_csv.short_description = 'Экспортировать в CSV'
    
    def download_report(self, obj):
        return format_html(
            '<a class="button" href="{}">Скачать отчет</a>',
            f'/admin/women/contest/{obj.id}/download-report/'
        )
    download_report.short_description = 'Отчет'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:contest_id>/download-report/',
                self.admin_site.admin_view(self.download_report_view),
                name='contest-download-report',
            ),
        ]
        return custom_urls + urls
    
    def download_report_view(self, request, contest_id):
        return generate_contest_report(contest_id)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_full_name', 'contest', 'created_at', 'is_reviewed', 'average_score', 'review_button')
    list_filter = (ReviewedFilter, 'contest')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'contest__title')
    ordering = ('-created_at',)
    inlines = [ApplicationAnswerInline, ReviewInline]
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    
    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"
    get_full_name.short_description = 'Участник'
    
    def average_score(self, obj):
        score = obj.reviews.aggregate(Avg('total_score'))['total_score__avg'] or 0
        return f"{score:.1f}"
    average_score.short_description = 'Средний балл'
    
    def is_reviewed(self, obj):
        return obj.reviews.exists()
    is_reviewed.boolean = True
    is_reviewed.short_description = 'Оценено'
    
    def review_button(self, obj):
        return format_html('<a href="/admin/women/review/add/?application={}" class="button">Оценить</a>', obj.id)
    review_button.short_description = 'Действия'
    review_button.allow_tags = True
    
    actions = ['export_applications_to_csv']
    
    def export_applications_to_csv(self, request, queryset):
        fields = ['Логин', 'Участник', 'Конкурс', 'Дата создания', 'Оценено', 'Средний балл']
        return export_to_csv(self, request, queryset, fields, 'applications.csv')
    export_applications_to_csv.short_description = 'Экспортировать в CSV'

@admin.register(ApplicationProxy)
class ApplicationProxyAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_full_name', 'contest', 'created_at', 'is_reviewed', 'average_score')
    list_filter = (ReviewedFilter, 'contest')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'contest__title')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    
    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"
    get_full_name.short_description = 'Участник'
    
    def average_score(self, obj):
        score = obj.reviews.aggregate(Avg('total_score'))['total_score__avg'] or 0
        return f"{score:.1f}"
    average_score.short_description = 'Средний балл'
    
    def is_reviewed(self, obj):
        return obj.reviews.exists()
    is_reviewed.boolean = True
    is_reviewed.short_description = 'Оценено'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(avg_score=Avg('reviews__total_score')).order_by('-avg_score')
    
    actions = ['export_rating_to_csv']
    
    def export_rating_to_csv(self, request, queryset):
        fields = ['Логин', 'Участник', 'Конкурс', 'Дата создания', 'Оценено', 'Средний балл']
        return export_to_csv(self, request, queryset, fields, 'rating.csv')
    export_rating_to_csv.short_description = 'Экспортировать в CSV'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'reviewer', 'total_score')
    list_filter = ('application__contest', 'reviewer')
    search_fields = ('application__user__username', 'reviewer__username')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Оценка', {
                'fields': ('application', 'reviewer', 'innovation', 'feasibility', 'impact', 'presentation_quality', 'total_score', 'comment'),
            }),
        ]
        
        # Добавляем информацию о заявке только если есть application_id в URL
        if 'application' in request.GET:
            fieldsets.insert(0, ('Информация о заявке', {
                'fields': ('application_info',),
                'classes': ('wide',),
            }))
                
        return fieldsets
    
    readonly_fields = ('application_info',)
    
    def application_info(self, obj=None):
        try:
            if 'application' in self.request.GET:
                application = Application.objects.get(id=self.request.GET['application'])
                
                html = f"""
                <div style="margin: 10px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; border: 1px solid #dee2e6;">
                    <h3 style="color: #6f42c1; margin-bottom: 15px;">Информация о заявке</h3>
                    <p style="margin: 5px 0;"><strong>Конкурс:</strong> {application.contest.title}</p>
                    <p style="margin: 5px 0;"><strong>Участник:</strong> {application.user.get_full_name()}</p>
                    <p style="margin: 5px 0;"><strong>Дата подачи:</strong> {application.created_at.strftime('%d.%m.%Y')}</p>
                    <h4 style="color: #6f42c1; margin: 15px 0 10px;">Ответы на вопросы:</h4>
                """
                
                answers = application.answers.all()
                if not answers:
                    html += "<p>Ответы на вопросы отсутствуют</p>"
                else:
                    for answer in answers:
                        html += f"""
                        <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 4px;">
                            <strong>{answer.field.label}:</strong> {answer.value}
                        </div>
                        """
                html += "</div>"
                return format_html(html)
            return "Информация о заявке будет доступна после выбора заявки"
        except Exception as e:
            return format_html(f"Ошибка при отображении информации: {str(e)}")
    application_info.short_description = 'Информация о заявке'
    
    def get_form(self, request, obj=None, **kwargs):
        self.request = request
        return super().get_form(request, obj, **kwargs)
    
    actions = ['export_reviews_to_csv']
    
    def export_reviews_to_csv(self, request, queryset):
        fields = ['Заявка', 'Эксперт', 'Общий балл']
        return export_to_csv(self, request, queryset, fields, 'reviews.csv')
    export_reviews_to_csv.short_description = 'Экспортировать в CSV'