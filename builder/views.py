from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ProfileForm, ResumeForm
from .models import Profile, Resume, NewsItem


def home(request):
    return render(request, 'home.html', {'news_items': NewsItem.objects.order_by('-created_at')[:3]})


def templates_list(request):
    templates = [
        {'slug': 'classic', 'name': 'Класичний', 'description': 'Чистий і офіційний стиль для будь-якої сфери.'},
        {'slug': 'it', 'name': 'IT', 'description': 'Сучасний шаблон для розробників і технічних спеціалістів.'},
        {'slug': 'manager', 'name': 'Менеджер', 'description': 'Підходить для управлінців і командних ролей.'},
    ]
    return render(request, 'templates.html', {'templates': templates})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error('username', 'Користувач з таким імʼям уже існує')
                messages.error(request, 'Реєстрація не вдалася. Спробуйте інше імʼя користувача.')
            else:
                Profile.objects.get_or_create(user=user, defaults={'full_name': user.username})
                login(request, user)
                messages.success(request, 'Акаунт створено')
                return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Невірний логін або пароль')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_list(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'full_name': request.user.username})
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено')
            return redirect('profile_list')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form, 'profile': profile})


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'resume_list.html', {'resumes': resumes})


@login_required
def resume_create(request):
    selected_template = request.session.get('selected_template', '')
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.template_name = selected_template
            resume.save()
            request.session.pop('selected_template', None)
            return redirect('resume_detail', pk=resume.pk)
    else:
        form = ResumeForm()
    return render(request, 'resume_form.html', {'form': form, 'title': 'Створити резюме', 'selected_template': selected_template})


@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    return render(request, 'resume_detail.html', {'resume': resume})


@login_required
def resume_edit(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('resume_detail', pk=resume.pk)
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'resume_form.html', {'form': form, 'title': 'Редагувати резюме'})


@login_required
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        return redirect('resume_list')
    return render(request, 'resume_confirm_delete.html', {'resume': resume})


@login_required
def export_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    content = f"{resume.title}\n\nКороткий опис:\n{resume.summary or 'Н/Д'}\n\nДосвід:\n{resume.experience or 'Н/Д'}\n\nОсвіта:\n{resume.education or 'Н/Д'}\n\nНавички:\n{resume.skills or 'Н/Д'}"
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{resume.title}.txt"'
    return response


def news_list(request):
    items = NewsItem.objects.order_by('-created_at')
    return render(request, 'news.html', {'items': items})


@login_required
def choose_template(request, slug):
    templates = {'classic': 'Класичний', 'it': 'IT', 'manager': 'Менеджер'}
    if slug not in templates:
        return redirect('templates_list')
    request.session['selected_template'] = slug
    messages.success(request, f'Обрано шаблон: {templates[slug]}')
    return redirect('resume_create')


@user_passes_test(lambda user: user.is_superuser)
def custom_admin_dashboard(request):
    resumes = Resume.objects.order_by('-updated_at')
    return render(request, 'custom_admin.html', {'resumes': resumes})


@user_passes_test(lambda user: user.is_superuser)
@require_POST
def admin_resume_action(request, pk, action):
    resume = get_object_or_404(Resume, pk=pk)
    if action == 'approve':
        resume.status = 'approved'
        resume.is_public = True
    elif action == 'reject':
        resume.status = 'rejected'
        resume.is_public = False
    elif action == 'delete':
        resume.delete()
        messages.success(request, 'Резюме видалено')
        return redirect('custom_admin_dashboard')
    else:
        return redirect('custom_admin_dashboard')

    resume.save()
    messages.success(request, 'Статус резюме оновлено')
    return redirect('custom_admin_dashboard')


@user_passes_test(lambda user: user.is_superuser)
def admin_resumes(request):
    resumes = Resume.objects.order_by('-updated_at')
    return render(request, 'admin_resumes.html', {'resumes': resumes})
