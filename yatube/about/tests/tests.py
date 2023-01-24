from http import HTTPStatus

from django.test import TestCase


class StaticPagesTests(TestCase):
    def test_static_pages(self):
        """Тестируем доступность статичных страниц author, tech"""
        static_pages = ['/about/author/', '/about/tech/']
        for page in static_pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)
