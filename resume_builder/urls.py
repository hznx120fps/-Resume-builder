from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from builder import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('templates/', views.templates_list, name='templates_list'),
    path('templates/<slug:slug>/', views.choose_template, name='choose_template'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin-resumes/', views.admin_resumes, name='admin_resumes'),
    path('admin-resume/<int:pk>/', views.admin_resume_detail, name='admin_resume_detail'),
    path('admin-resumes/<int:pk>/<str:action>/', views.admin_resume_action, name='admin_resume_action'),
    path('custom-admin/online/', views.admin_online_users, name='admin_online_users'),
    path('custom-admin/users/', views.admin_user_access, name='admin_user_access'),
    path('custom-admin/users/<int:pk>/access/', views.admin_user_access_action, name='admin_user_access_action'),
    path('custom-admin/profile/<int:pk>/', views.admin_profile_detail, name='admin_profile_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<str:username>/', views.profile_view, name='profile_view'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/new/', views.resume_create, name='resume_create'),
    path('resumes/<int:pk>/', views.resume_detail, name='resume_detail'),
    path('resumes/public/<int:pk>/', views.resume_public_detail, name='resume_public_detail'),
    path('resumes/<int:pk>/edit/', views.resume_edit, name='resume_edit'),
    path('resumes/<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('resumes/<int:pk>/export/', views.export_resume, name='export_resume'),
    path('resumes/archived/', views.resume_archived, name='resume_archived'),
    path('resumes/<int:pk>/restore/', views.resume_restore, name='resume_restore'),
    path('resumes/<int:pk>/permanent-delete/', views.resume_permanent_delete, name='resume_permanent_delete'),
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/json/', views.news_json, name='news_json'),
    path('news/<int:pk>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
