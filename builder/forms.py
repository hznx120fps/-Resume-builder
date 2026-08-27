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


class ResumeForm(forms.ModelForm):
    summary = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    experience = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    education = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    skills = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))

    class Meta:
        model = Resume
        fields = ('title', 'summary', 'experience', 'education', 'skills', 'is_public')


class NewsForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = NewsItem
        fields = ('title', 'content', 'image', 'category', 'status', 'is_pinned')


class AdminAccessForm(forms.Form):
    is_staff = forms.BooleanField(required=False, label='Доступ до кастомної адмін-панелі')
