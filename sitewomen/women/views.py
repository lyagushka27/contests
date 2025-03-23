from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, ApplicationForm, Application, UserProfile
from django.db.models import Avg
from .models import Application
from .generations_pdf import generate_certificate

def index(request):
    data = {'title': 'Главная страница'}
    return render(request, 'index.html', data)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def form(request):
    return render(request, 'application_form.html', {'title': 'Форма заявки'})

def application_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('success')
    else:
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        form = ApplicationForm(initial={
            'first_name': user_profile.first_name,
            'middle_name': user_profile.middle_name,
            'last_name': user_profile.last_name,
            'email': request.user.email,
        })
    return render(request, 'application_form.html', {'form': form})

def success_view(request):
    return render(request, 'success.html', {'title': 'Успех'})

def my_applications(request):
    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        return render(request, 'my_applications.html', {'applications': applications})
    else:
        return redirect('login')

def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'application_detail.html', {'application': application})

@login_required
def download_certificate(request):
    applications = Application.objects.filter(user=request.user)
    for application in applications:
        if application.is_reviewed():
            contest_name = "Конкурс" 
            return generate_certificate(request.user, contest_name, is_winner=False)
    return HttpResponse("Проект еще не оценен.", status=403)

@login_required
def download_diploma(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    contest_name = "Конкурс"  
    if is_top_10(application):
        return generate_certificate(request.user, contest_name, is_winner=True)
    else:
        return HttpResponse("Участник не входит в топ-10.", status=403)

def is_top_10(application):
    top_applications = Application.objects.annotate(average_score=Avg('reviews__total_score')).order_by('-average_score')[:10]
    return application in top_applications