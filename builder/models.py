from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    GRADIENT_DIRECTIONS = [
        ('90deg', 'Зліва направо'),
        ('135deg', 'Діагональ'),
        ('180deg', 'Зверху вниз'),
        ('270deg', 'Справа наліво'),
    ]
    THEME_CHOICES = [
        ('light', 'Світла'),
        ('dark', 'Темна'),
        ('system', 'Системна'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    primary_color = models.CharField(max_length=7, default='#0d6efd')
    secondary_color = models.CharField(max_length=7, default='#6f42c1')
    accent_color = models.CharField(max_length=7, default='#dc3545')
    background_color = models.CharField(max_length=7, default='#f8f9fa')
    gradient_direction = models.CharField(max_length=30, choices=GRADIENT_DIRECTIONS, default='135deg')
    gradient_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name or self.user.username


class Resume(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На перевірці'),
        ('approved', 'Прийнято'),
        ('rejected', 'Відхилено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    template_name = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class NewsItem(models.Model):
    CATEGORY_CHOICES = [
        ('updates', 'Оновлення сервісу'),
        ('features', 'Нові функції'),
        ('tips', 'Поради'),
        ('templates', 'Шаблони резюме'),
    ]
    STATUS_CHOICES = [
        ('published', 'Опубліковано'),
        ('draft', 'Чернетка'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_items')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='updates')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='published')
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    EVENT_CHOICES = [
        ('login', 'Вхід'),
        ('news_created', 'Новину створено'),
        ('news_updated', 'Новину змінено'),
        ('news_deleted', 'Новину видалено'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.message
