import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from resume_builder.env_utils import load_environment

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

    def test_resume_can_be_downloaded_as_pdf(self):
        user = get_user_model().objects.create_user(username='pdfuser', password='Test@1234')
        resume = Resume.objects.create(user=user, title='Моє резюме', summary='Український текст')
        self.client.force_login(user)

        response = self.client.get(reverse('export_resume_pdf', args=[resume.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('filename="resume.pdf"', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_resume_can_be_cloned(self):
        user = get_user_model().objects.create_user(username='cloneuser', password='Test@1234')
        resume = Resume.objects.create(
            user=user,
            title='Основне резюме',
            summary='Коротко про мене',
            experience='2 роки роботи',
            education='Вища освіта',
            skills='Python, Django',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('resume_clone', args=[resume.pk]))

        self.assertEqual(response.status_code, 302)
        cloned = Resume.objects.filter(user=user, title='Основне резюме (Копія)').first()
        self.assertIsNotNone(cloned)
        self.assertEqual(cloned.summary, 'Коротко про мене')
        self.assertEqual(cloned.skills, 'Python, Django')

    def test_resume_can_be_downloaded_as_docx(self):
        user = get_user_model().objects.create_user(username='docxuser', password='Test@1234')
        resume = Resume.objects.create(user=user, title='Резюме для DOCX', summary='Текст для Word')
        self.client.force_login(user)

        response = self.client.get(reverse('export_resume_docx', args=[resume.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', response['Content-Type'])
        self.assertIn('filename="resume-dlya-docx.docx"', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'PK'))


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


class EmailEnvTests(TestCase):
    def test_load_environment_reads_dotenv_file(self):
        env_path = Path('C:/temp/resume_builder_test_env')
        env_path.mkdir(parents=True, exist_ok=True)
        env_file = env_path / '.env'
        env_file.write_text('EMAIL_HOST=smtp.gmail.com\nEMAIL_PORT=587\n', encoding='utf-8')

        original = os.environ.get('EMAIL_HOST')
        original_port = os.environ.get('EMAIL_PORT')
        try:
            os.environ.pop('EMAIL_HOST', None)
            os.environ.pop('EMAIL_PORT', None)
            load_environment(env_path)
            self.assertEqual(os.environ['EMAIL_HOST'], 'smtp.gmail.com')
            self.assertEqual(os.environ['EMAIL_PORT'], '587')
        finally:
            if original is None:
                os.environ.pop('EMAIL_HOST', None)
            else:
                os.environ['EMAIL_HOST'] = original

            if original_port is None:
                os.environ.pop('EMAIL_PORT', None)
            else:
                os.environ['EMAIL_PORT'] = original_port

            if env_file.exists():
                env_file.unlink()
