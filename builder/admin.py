from django.contrib import admin
from .models import Profile, Resume, NewsItem


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'title', 'email')
    search_fields = ('full_name', 'user__username', 'email')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'template_name', 'is_public', 'updated_at')
    list_filter = ('is_public', 'template_name')
    search_fields = ('title', 'user__username', 'summary')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
