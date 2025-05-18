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
    path('my_applications/', views.contest_list, name='my_applications'),
    path('application_detail/<int:application_id>/', views.application_detail, name='application_detail'),
    path('download_certificate/', views.download_certificate, name='download_certificate'),
    path('download_diploma/', views.download_diploma, name='download_diploma'),
    path('contests/', views.contest_list, name='contest_list'),
    path('contest/<int:contest_id>/', views.contest_detail, name='contest_detail'),
    # path('create_application/<int:contest_id>/', views.create_application, name='create_application'),
    path('view_application/<int:contest_id>/', views.view_application, name='view_application'),
    path('contest/<int:contest_id>/apply/', views.contest_application, name='contest_application'),
    path('application/<int:application_id>/review/', views.review_application, name='review_application'),
    path('contest/<int:contest_id>/download-certificate/', views.download_certificate, name='download_certificate'),
    path('contest/<int:contest_id>/download-diploma/', views.download_diploma, name='download_diploma'),
]