from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template.loader import render_to_string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, ApplicationForm, Application

def index(request):
    data = {'title': 'Главная страница'}
    return render(request, 'index.html', data)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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
            # Создаем объект Application, но не сохраняем его сразу
            application = form.save(commit=False)
            # Устанавливаем текущего пользователя
            application.user = request.user
            # Сохраняем объект в базу данных
            application.save()
            return redirect('success')  # Перенаправьте на страницу успеха после отправки
    else:
        form = ApplicationForm()

    return render(request, 'application_form.html', {'title': 'Заявка на конкурс', 'form': form})

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
