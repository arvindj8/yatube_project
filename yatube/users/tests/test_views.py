from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from posts.models import User


class UsersViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NonameUser',
                                            email='test@yandex.ru')

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def _get_token(self):
        form_data = {'email': self.user.email}
        response = self.client.post(reverse('users:password_reset'),
                                    data=form_data, follow=True)
        token = response.context.get('csrf_token')
        return token

    def test_templates_users_views(self):
        """Тестируем, что users/view используют соответствующий шаблон"""
        # Получаем uid
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        templates_uses = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('login'),
            'users/password_change_form.html':
                reverse('users:password_change'),
            'users/password_change_done.html':
                reverse('users:password_change_done'),
            'users/password_reset_form.html':
                reverse('users:password_reset'),
            'users/password_reset_done.html':
                reverse('users:password_reset_done'),
            'users/password_reset_confirm.html':
                reverse('users:password_reset_confirm',
                        kwargs={'uidb64': uid, 'token': self._get_token()}),
            'users/password_reset_complete.html':
                reverse('users:password_reset_complete'),
            'users/logged_out.html': reverse('users:logout')
        }

        for template, url in templates_uses.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_form_signup_true(self):
        """Тестируем, что на страницу регистрации
        передается соответствующую форма"""
        response = self.guest_user.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
