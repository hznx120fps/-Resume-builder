from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Resume, NewsItem


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Користувач з таким email вже використовується')
        return email


class ProfileForm(forms.ModelForm):
    photo = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ('full_name', 'title', 'email', 'phone', 'location', 'bio', 'photo')


class AppearanceForm(forms.ModelForm):
    primary_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    secondary_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    accent_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))
    background_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Profile
        fields = ('theme', 'primary_color', 'secondary_color', 'accent_color', 'background_color', 'gradient_direction', 'gradient_enabled')


def format_custom_sections(sections):
    if not sections:
        return ''
    lines = []
    for item in sections:
        if isinstance(item, dict):
            title = (item.get('title') or '').strip()
            content = (item.get('content') or '').strip()
            if title or content:
                lines.append(f"{title}: {content}")
    return '\n'.join(lines)


class ResumeForm(forms.ModelForm):
    summary = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    experience = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    education = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    skills = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    custom_sections = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label='Додаткові секції',
        help_text='Формат: Назва секції: опис секції. Кожна секція з нового рядка.'
    )

    class Meta:
        model = Resume
        fields = ('title', 'summary', 'experience', 'education', 'skills', 'custom_sections', 'is_public')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.custom_sections:
            self.fields['custom_sections'].initial = format_custom_sections(self.instance.custom_sections)

    def clean_custom_sections(self):
        raw_value = self.cleaned_data.get('custom_sections', '')
        sections = []
        for line in (raw_value or '').splitlines():
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                title, content = line.split(':', 1)
            elif '|' in line:
                title, content = line.split('|', 1)
            else:
                continue
            title = title.strip()
            content = content.strip()
            if title or content:
                sections.append({'title': title or 'Секція', 'content': content})
        return sections

    def save(self, commit=True):
        resume = super().save(commit=False)
        resume.custom_sections = self.cleaned_data.get('custom_sections', [])
        if commit:
            resume.save()
        return resume


class NewsForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = NewsItem
        fields = ('title', 'content', 'image', 'category', 'status', 'is_pinned')


class AdminAccessForm(forms.Form):
    is_staff = forms.BooleanField(required=False, label='Доступ до кастомної адмін-панелі')
