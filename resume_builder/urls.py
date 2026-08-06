from django.contrib import admin
from django.urls import path
from builder import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('templates/', views.templates_list, name='templates_list'),
    path('templates/<slug:slug>/', views.choose_template, name='choose_template'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin-resumes/', views.admin_resumes, name='admin_resumes'),
    path('admin-resumes/<int:pk>/<str:action>/', views.admin_resume_action, name='admin_resume_action'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profiles/', views.profile_list, name='profile_list'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/new/', views.resume_create, name='resume_create'),
    path('resumes/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('resumes/<int:pk>/edit/', views.resume_edit, name='resume_edit'),
    path('resumes/<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('resumes/<int:pk>/export/', views.export_resume, name='export_resume'),
    path('news/', views.news_list, name='news_list'),
]
