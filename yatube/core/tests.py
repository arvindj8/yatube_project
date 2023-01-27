from http import HTTPStatus

from django.test import Client, TestCase


class TestsPagesErrors(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_user = Client()

    def test_page_404_show_error(self):
        """Тестируем, что если страница не найдена вызывается страница 404"""
        response = self.guest_user.get('http://127.0.0.1:8000/hhhkk')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page_404_show_template(self):
        """Тестируем, что page404 использует соответствующий html шаблон"""
        response = self.guest_user.get('http://127.0.0.1:8000/hhhkk')
        self.assertTemplateUsed(response, 'core/404.html')