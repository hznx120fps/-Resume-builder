from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ActivityLog, NewsItem, Profile, Resume


class RegistrationTests(TestCase):
    def test_duplicate_username_shows_form_error(self):
        get_user_model().objects.create_user(
            username='testuser',
            email='first@example.com',
            password='Test@1234',
        )

        response = self.client.post(
            reverse('register'),
            {
                'username': 'testuser',
                'email': 'second@example.com',
                'password1': 'Test@1234',
                'password2': 'Test@1234',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'вже існує')

    def test_duplicate_email_shows_form_error(self):
        get_user_model().objects.create_user(
            username='firstuser',
            email='shared@example.com',
            password='Test@1234',
        )

        response = self.client.post(
            reverse('register'),
            {
                'username': 'seconduser',
                'email': 'shared@example.com',
                'password1': 'Test@1234',
                'password2': 'Test@1234',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'вже використовується')


class TemplateSelectionTests(TestCase):
    def test_templates_page_lists_popular_templates(self):
        response = self.client.get(reverse('templates_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Класичний')
        self.assertContains(response, 'IT')

    def test_resume_creation_saves_selected_template(self):
        user = get_user_model().objects.create_user(username='templateuser', password='Test@1234')
        self.client.force_login(user)
        session = self.client.session
        session['selected_template'] = 'it'
        session.save()

        response = self.client.post(
            reverse('resume_create'),
            {'title': 'Моє резюме', 'summary': 'Сумарний опис', 'experience': '', 'education': '', 'skills': ''},
        )

        self.assertEqual(response.status_code, 302)
        resume = Resume.objects.get(title='Моє резюме')
        self.assertEqual(resume.template_name, 'it')


class AppearanceAndNewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='viewer', password='Test@1234')
        self.admin = get_user_model().objects.create_user(username='editor', password='Test@1234', is_staff=True)

    def test_appearance_settings_are_saved(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('settings'), {
            'theme': 'dark',
            'primary_color': '#112233',
            'secondary_color': '#445566',
            'accent_color': '#778899',
            'background_color': '#101010',
            'gradient_direction': '90deg',
            'gradient_enabled': 'on',
        })

        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.theme, 'dark')
        self.assertEqual(profile.secondary_color, '#445566')
        self.assertEqual(profile.gradient_direction, '90deg')

    def test_public_news_hides_drafts_and_login_is_logged(self):
        published = NewsItem.objects.create(title='Visible', content='Published')
        NewsItem.objects.create(title='Hidden', content='Draft', status='draft')
        response = self.client.get(reverse('news_list'))

        self.assertContains(response, published.title)
        self.assertNotContains(response, 'Hidden')
        self.client.post(reverse('login'), {'username': 'viewer', 'password': 'Test@1234'})
        self.assertTrue(ActivityLog.objects.filter(event_type='login', user=self.user).exists())
