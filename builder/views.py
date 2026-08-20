from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import RegisterForm, ProfileForm, ResumeForm, NewsForm, AdminAccessForm
from .models import Profile, Resume, NewsItem
from datetime import timedelta


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
    resumes = Resume.objects.filter(user=request.user, is_deleted=False).order_by('-updated_at')
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
    resume = get_object_or_404(Resume, pk=pk, user=request.user, is_deleted=False)
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
        resume.is_deleted = True
        resume.save()
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
    form = None
    if request.user.is_authenticated and request.user.is_staff:
        form = NewsForm()
    return render(request, 'news.html', {'items': items, 'form': form})


@user_passes_test(lambda user: user.is_staff)
@require_POST
def create_news(request):
    form = NewsForm(request.POST, request.FILES)
    if form.is_valid():
        news = form.save(commit=False)
        news.author = request.user
        news.save()
        messages.success(request, 'Новина додана')
    else:
        messages.error(request, 'Помилка при додаванні новини')
    return redirect('news_list')


def news_json(request):
    items = NewsItem.objects.order_by('-created_at')[:20]
    data = []
    for it in items:
        data.append({
            'id': it.pk,
            'title': it.title,
            'content': it.content,
            'created_at': it.created_at.isoformat(),
            'image_url': it.image.url if it.image else None,
            'author': it.author.username if it.author else None,
            'author_profile_url': reverse('profile_view', args=[it.author.username]) if it.author else None,
        })
    return JsonResponse({'items': data})


@user_passes_test(lambda user: user.is_staff)
def edit_news(request, pk):
    news = get_object_or_404(NewsItem, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новина оновлена')
            return redirect('news_list')
    else:
        form = NewsForm(instance=news)
    return render(request, 'news_edit.html', {'form': form, 'news': news})


@user_passes_test(lambda user: user.is_staff)
@require_POST
def delete_news(request, pk):
    news = get_object_or_404(NewsItem, pk=pk)
    news.delete()
    messages.success(request, 'Новина видалена')
    return redirect('news_list')


@login_required
def choose_template(request, slug):
    templates = {'classic': 'Класичний', 'it': 'IT', 'manager': 'Менеджер'}
    if slug not in templates:
        return redirect('templates_list')
    request.session['selected_template'] = slug
    messages.success(request, f'Обрано шаблон: {templates[slug]}')
    return redirect('resume_create')


@user_passes_test(lambda user: user.is_staff)
def custom_admin_dashboard(request):
    resumes = Resume.objects.order_by('-updated_at')
    # compute online users in last 5 minutes
    cutoff = timezone.now() - timedelta(minutes=5)
    online_count = Profile.objects.filter(last_seen__gte=cutoff).count()
    return render(request, 'custom_admin.html', {'resumes': resumes})


@user_passes_test(lambda user: user.is_staff)
@require_POST
def admin_resume_action(request, pk, action):
    resume = get_object_or_404(Resume, pk=pk)
    # idempotent server-side handling: if already in target state, do nothing
    if action == 'approve':
        if resume.status != 'approved':
            resume.status = 'approved'
            resume.is_public = True
            resume.save()
            messages.success(request, 'Резюме прийнято')
        else:
            messages.info(request, 'Резюме вже прийнято')
        return redirect('custom_admin_dashboard')

    if action == 'reject':
        if resume.status != 'rejected':
            resume.status = 'rejected'
            resume.is_public = False
            resume.save()
            messages.success(request, 'Резюме відхилено')
        else:
            messages.info(request, 'Резюме вже відхилено')
        return redirect('custom_admin_dashboard')

    if action == 'delete':
        # if already archived, perform hard delete; otherwise archive (soft-delete)
        if resume.is_deleted:
            resume.delete()
            messages.success(request, 'Резюме видалено назавжди')
        else:
            resume.is_deleted = True
            resume.save()
            messages.success(request, 'Резюме переміщено в архів')
        return redirect('custom_admin_dashboard')

    if action == 'restore':
        if resume.is_deleted:
            resume.is_deleted = False
            resume.save()
            messages.success(request, 'Резюме відновлено')
        else:
            messages.info(request, 'Резюме не в архіві')
        return redirect('custom_admin_dashboard')

    return redirect('custom_admin_dashboard')


@user_passes_test(lambda user: user.is_staff)
def admin_resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    # also show other resumes from the same user
    others = Resume.objects.filter(user=resume.user).exclude(pk=resume.pk).order_by('-updated_at')
    return render(request, 'admin_resume_detail.html', {'resume': resume, 'others': others})


@user_passes_test(lambda user: user.is_staff)
def admin_resumes(request):
    resumes = Resume.objects.order_by('-updated_at')
    return render(request, 'admin_resumes.html', {'resumes': resumes})


@user_passes_test(lambda user: user.is_staff)
def admin_online_users(request):
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(minutes=5)
    profiles = Profile.objects.filter(last_seen__gte=cutoff).select_related('user').order_by('-last_seen')
    return render(request, 'admin_online.html', {'profiles': profiles, 'cutoff': cutoff})


@user_passes_test(lambda user: user.is_superuser)
def admin_user_access(request):
    users = User.objects.order_by('username')
    return render(request, 'admin_user_access.html', {'users': users})


@user_passes_test(lambda user: user.is_superuser)
@require_POST
def admin_user_access_action(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.info(request, 'Не можна забрати доступ у поточного superuser')
    else:
        user.is_staff = request.POST.get('is_staff') == '1'
        user.save(update_fields=['is_staff'])
        messages.success(request, f'Доступ для {user.username} оновлено')
    return redirect('admin_user_access')


@user_passes_test(lambda user: user.is_staff)
def admin_profile_detail(request, pk):
    """Admin view: inspect a user's profile and their resumes."""
    profile = get_object_or_404(Profile, pk=pk)
    resumes = Resume.objects.filter(user=profile.user).order_by('-updated_at')
    return render(request, 'admin_profile_detail.html', {'profile': profile, 'resumes': resumes})


def profile_view(request, username):
    """Public (or user) view of a profile. Shows public resumes only."""
    profile = get_object_or_404(Profile, user__username=username)
    resumes = Resume.objects.filter(user=profile.user, is_public=True, is_deleted=False).order_by('-updated_at')
    return render(request, 'profile_view.html', {'profile': profile, 'resumes': resumes})


def resume_public_detail(request, pk):
    """Public view of a resume that has been approved/published by admin."""
    resume = get_object_or_404(Resume, pk=pk, is_public=True, is_deleted=False)
    return render(request, 'resume_detail.html', {'resume': resume})


@login_required
def resume_archived(request):
    """List archived resumes for the current user with restore/delete actions."""
    resumes = Resume.objects.filter(user=request.user, is_deleted=True).order_by('-updated_at')
    return render(request, 'resume_archived.html', {'resumes': resumes})


@login_required
@require_POST
def resume_restore(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if resume.is_deleted:
        resume.is_deleted = False
        resume.save()
        messages.success(request, 'Резюме відновлено')
    else:
        messages.info(request, 'Резюме не у архіві')
    return redirect('resume_archived')


@login_required
@require_POST
def resume_permanent_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if resume.is_deleted:
        resume.delete()
        messages.success(request, 'Резюме видалено назавжди')
    else:
        messages.error(request, 'Спочатку помістіть резюме в архів')
    return redirect('resume_archived')
