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


class ResumeForm(forms.ModelForm):
    summary = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    experience = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    education = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    skills = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))

    class Meta:
        model = Resume
        fields = ('title', 'summary', 'experience', 'education', 'skills', 'is_public')


class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ('title', 'content')
