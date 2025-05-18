from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, ApplicationForm, Application, UserProfile, ContestForm, ReviewForm
from django.db.models import Avg
from .models import Application, Contest, ApplicationAnswer, Review
from .generations_pdf import generate_certificate
from django import forms
from django.utils import timezone

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

def application_view(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)  # Получаем конкурс
    form_class = build_application_form(contest)  # Создаем форму для этого конкурса

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.contest = contest
            application.save()
            return redirect('success')
    else:
        form = form_class()  # Отображаем форму при GET-запросе

    return render(request, 'application_form.html', {'form': form, 'contest': contest})


def success_view(request):
    return render(request, 'success.html', {'title': 'Успех'})

def my_applications(request):
    if request.user.is_authenticated:
        applications = Application.objects.filter(user=request.user)
        contests = Contest.objects.all()
        return render(request, 'my_applications.html', {'applications': applications, 'contests': contests})
    else:
        return redirect('login')

def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'application_detail.html', {'application': application})

@login_required
def download_certificate(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    application = get_object_or_404(Application, user=request.user, contest=contest)
    
    if application.is_reviewed():
        return generate_certificate(request.user, contest.title, is_winner=False)
    return HttpResponse("Проект еще не оценен.", status=403)

@login_required
def download_diploma(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    application = get_object_or_404(Application, user=request.user, contest=contest)
    
    if application.is_reviewed() and is_top_10(application):
        return generate_certificate(request.user, contest.title, is_winner=True)
    return HttpResponse("Участник не входит в топ-10 или проект еще не оценен.", status=403)

def is_top_10(application):
    top_applications = Application.objects.annotate(average_score=Avg('reviews__total_score')).order_by('-average_score')[:10]
    return application in top_applications

def contest_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    contests = Contest.objects.all()
    contest_data = []
    
    for contest in contests:
        # Проверяем наличие заявки для текущего пользователя и конкурса
        has_application = Application.objects.filter(
            user=request.user, 
            contest=contest
        ).exists()
        
        # Добавляем отладочную информацию
        print(f"Contest {contest.id}: {contest.title}")
        print(f"Has application: {has_application}")
        
        contest_data.append({
            'contest': contest,
            'has_application': has_application
        })
    
    # Добавляем отладочную информацию о всех данных
    print("\nAll contest data:")
    for item in contest_data:
        print(f"Contest: {item['contest'].title}")
        print(f"Has application: {item['has_application']}\n")
    
    return render(request, 'women/my_applications.html', {
        'contests': contest_data,
        'now': timezone.now().date()  # Добавляем текущую дату в контекст
    })

def contest_detail(request, contest_id):
    try:
        contest = Contest.objects.get(id=contest_id)
        application = None
        
        if request.user.is_authenticated:
            application = Application.objects.filter(user=request.user, contest=contest).first()
        
        return render(request, 'women/contest_detail.html', {
            'contest': contest,
            'application': application
        })
    except Contest.DoesNotExist:
        # Если конкурс не найден, перенаправляем на список конкурсов
        return redirect('contest_list')

@login_required
def create_application(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    if Application.objects.filter(user=request.user, contest=contest).exists():
        return redirect('contest_list')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.contest = contest
            application.save()
            return redirect('contest_list')
    else:
        form = ApplicationForm()

    return render(request, 'application_form.html', {'form': form, 'contest': contest})

@login_required
def view_application(request, contest_id):
    try:
        # Получаем заявку для текущего пользователя и конкурса
        application = Application.objects.get(
            user=request.user, 
            contest_id=contest_id
        )
        
        # Получаем все ответы
        answers = application.answers.all()
        
        return render(request, 'women/application_detail.html', {
            'application': application,
            'answers': answers
        })
    except Application.DoesNotExist:
        # Если заявка не найдена, перенаправляем на страницу конкурса
        return redirect('contest_detail', contest_id=contest_id)


def build_application_form(contest):
    class DynamicApplicationForm(forms.Form):
        pass  # Мы создадим форму динамически

    # Перебираем все поля конкурса и создаем соответствующие поля формы
    for field in contest.fields.order_by('order'):
        if field.field_type == 'text':
            form_field = forms.CharField(label=field.label, required=field.required)
        elif field.field_type == 'email':
            form_field = forms.EmailField(label=field.label, required=field.required)
        elif field.field_type == 'number':
            form_field = forms.IntegerField(label=field.label, required=field.required)
        elif field.field_type == 'file':
            form_field = forms.FileField(label=field.label, required=field.required)
        elif field.field_type == 'image':
            form_field = forms.ImageField(label=field.label, required=field.required)
        elif field.field_type == 'choice':
            choices = [(c.value, c.value) for c in field.choices.all()]
            form_field = forms.ChoiceField(label=field.label, choices=choices, required=field.required)
        else:
            continue  # В случае других типов пропускаем создание поля

        # Добавляем созданное поле в динамическую форму
        DynamicApplicationForm.base_fields[field.name] = form_field

    return DynamicApplicationForm 

# def create_contest(request):
#     if request.method == 'POST':
#         form = ContestForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('contest_list')  # Перенаправление после успешного создания
#     else:
#         form = ContestForm()

#     return render(request, 'templates/application_form.html', {'form': form})

def contest_application(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    
    if request.method == 'POST':
        form = build_application_form(contest)(request.POST, request.FILES)
        if form.is_valid():
            # Создаем заявку
            application = Application.objects.create(
                user=request.user,
                contest=contest
            )
            
            # Сохраняем ответы на поля
            for field_name, value in form.cleaned_data.items():
                field = contest.fields.get(name=field_name)
                ApplicationAnswer.objects.create(
                    application=application,
                    field=field,
                    value=str(value)
                )
            return redirect('contest_detail', contest_id=contest.id)
    else:
        form = build_application_form(contest)()
    
    return render(request, 'women/application_form.html', {
        'form': form,
        'contest': contest
    })

@login_required
def review_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Проверяем, не оценивал ли уже эксперт эту заявку
    existing_review = Review.objects.filter(
        application=application,
        reviewer=request.user
    ).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.application = application
            review.reviewer = request.user
            review.save()
            return redirect('application_detail', application_id=application.id)
    else:
        form = ReviewForm(instance=existing_review)
    
    # Получаем все ответы заявки
    answers = application.answers.all()
    
    return render(request, 'women/review_application.html', {
        'form': form,
        'application': application,
        'answers': answers,
        'existing_review': existing_review
    })