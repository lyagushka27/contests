from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
import csv

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_superuser')
    
    def export_users_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=users.csv'
        response.write('\ufeff'.encode('utf-8'))
        
        writer = csv.writer(response)
        writer.writerow(['Логин', 'Имя', 'Фамилия', 'Email', 'Статус'])
        
        for user in queryset:
            writer.writerow([
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                'Администратор' if user.is_staff else 'Пользователь'
            ])
        
        return response
    export_users_to_csv.short_description = 'Экспортировать в CSV'
    
    actions = ['export_users_to_csv']

admin.site.unregister(User)
admin.site.register(User, UserAdmin) 