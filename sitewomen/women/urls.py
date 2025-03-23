from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.index, name = 'home'),
    path('reg/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('form/', views.application_view, name = 'form'),
    path('success/', views.success_view, name='success'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('application_detail/<int:application_id>/', views.application_detail, name='application_detail'),
    path('download_certificate/', views.download_certificate, name='download_certificate'),
    path('download_diploma/', views.download_diploma, name='download_diploma'),
]