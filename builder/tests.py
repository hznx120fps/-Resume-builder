from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Resume


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
