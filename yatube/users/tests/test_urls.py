from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import User


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NonameUser')

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def _assert_check_status_code_page(self, list_pages, status_auth,
                                       status_code_url):
        """Проверка статус кода страниц"""
        users_url_pages = list_pages
        for page in users_url_pages:
            response = status_auth.get(page)
            self.assertEqual(response.status_code, status_code_url)

    def test_access_url_pages_unauthorized_users(self):
        """Тестируем доступность всех страниц приложения Users
        для неавторизованных пользователей"""
        status_auth = self.guest_user
        status_code_url = HTTPStatus.OK
        users_url_pages = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
            '/auth/logout/'
        ]
        self._assert_check_status_code_page(users_url_pages, status_auth,
                                            status_code_url)

    def test_access_url_pages_authorized_users(self):
        """Тестируем доступность страниц приложения Users
        для авторизованных пользователей"""
        status_auth = self.authorized_client
        status_code_url = HTTPStatus.OK
        users_url_pages = [
            '/auth/password_change/',
            '/auth/password_change/done/'
        ]
        self._assert_check_status_code_page(users_url_pages, status_auth,
                                            status_code_url),

    def test_redirect_for_pages_auth_users(self):
        """Тестируем, что на страницах приложения Users, предназначенных для
        зарегистрированных пользователей происходит Redirect для анонимных"""
        status_auth = self.guest_user
        status_code_url = HTTPStatus.FOUND
        users_url_pages = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        self._assert_check_status_code_page(users_url_pages, status_auth,
                                            status_code_url)

    def test_urls_uses_correct_template(self):
        """Тестируем, что URL-адреса приложения Users
        использует соответствующий шаблон."""
        templates_uses = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_confirm.html':
                '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_complete.html': '/auth/reset/done/',
            'users/logged_out.html': '/auth/logout/'
        }

        for template, url in templates_uses.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
