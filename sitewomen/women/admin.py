from django.contrib import admin
from .models import Application

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('startup_name', 'user', 'nomination', 'created_at')
    search_fields = ('startup_name', 'user__username', 'nomination')
    list_filter = ('nomination', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Application, ApplicationAdmin)
