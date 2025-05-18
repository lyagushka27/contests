from django.contrib import admin
from django.utils.html import format_html
from .models import Review, Application

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
        
        # Если это форма создания новой оценки и есть application_id в URL
        if obj is None and 'application' in request.GET:
            try:
                application = Application.objects.get(id=request.GET['application'])
                # Добавляем информацию о заявке в начало формы
                fieldsets.insert(0, ('Информация о заявке', {
                    'fields': ('application_info',),
                    'classes': ('wide',),
                }))
            except Application.DoesNotExist:
                pass
                
        return fieldsets
    
    readonly_fields = ('application_info',)
    
    def application_info(self, obj=None):
        if obj is None and 'application' in self.request.GET:
            try:
                application = Application.objects.get(id=self.request.GET['application'])
                html = f"""
                <div style="margin: 10px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; border: 1px solid #dee2e6;">
                    <h3 style="color: #6f42c1; margin-bottom: 15px;">Информация о заявке</h3>
                    <p style="margin: 5px 0;"><strong>Конкурс:</strong> {application.contest.title}</p>
                    <p style="margin: 5px 0;"><strong>Участник:</strong> {application.user.get_full_name()}</p>
                    <p style="margin: 5px 0;"><strong>Дата подачи:</strong> {application.created_at.strftime('%d.%m.%Y')}</p>
                    <h4 style="color: #6f42c1; margin: 15px 0 10px;">Ответы на вопросы:</h4>
                """
                for answer in application.answers.all():
                    html += f"""
                    <div style="margin: 8px 0; padding: 8px; background-color: white; border-radius: 4px;">
                        <strong>{answer.field.label}:</strong> {answer.value}
                    </div>
                    """
                html += "</div>"
                return format_html(html)
            except Application.DoesNotExist:
                pass
        return "Информация о заявке будет доступна после сохранения"
    application_info.short_description = 'Информация о заявке'
    
    def get_form(self, request, obj=None, **kwargs):
        self.request = request
        return super().get_form(request, obj, **kwargs)
    
    actions = ['export_reviews_to_csv']
    
    def export_reviews_to_csv(self, request, queryset):
        fields = ['Заявка', 'Эксперт', 'Общий балл']
        return export_to_csv(self, request, queryset, fields, 'reviews.csv')
    export_reviews_to_csv.short_description = 'Экспортировать в CSV' 