from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса
        # posts/<post_id>/create/
        cls.user = User.objects.create_user(username='TestUser123')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=Group.objects.create(title='test title', slug='test_slug')
        )

    def setUp(self):
        cache.clear()
        # Создаем неавторизованный клиент
        self.guest_client = Client()

        # Создаем авторизованный клиент
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Создаем автора поста
        self.user_author = User.objects.get(username=self.post.author)
        self.posts_author = Client()
        self.posts_author.force_login(self.user_author)

    def test_posts_urls_unauthorized(self):
        """Тестируем доступность общедоступных страниц posts,
        для неавторизованного пользователя """
        template = [
            '/',
            f'/group/{self.post.group.slug}/',
            f'/profile/{self.post.author.username}/',
            f'/posts/{self.post.id}/',
        ]
        for url in template:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_urls_authorized(self):
        """Тестируем доступность страницы /create/
        для авторизованного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_urls_unauthorized(self):
        """Тестируем доступность страницы /create/
        для неавторизованного пользователя"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_edit_post(self):
        """Тестируем доступность страницы /edit/ только для автора поста"""
        response = self.posts_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Тестируем несуществующую страницу"""
        response = self.guest_client.get('/unexciting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates(self):
        """Тестируем что URL адрес использует соответствующий шаблон"""
        templates_uses = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for url, template in templates_uses.items():
            with self.subTest(url=url):
                response = self.posts_author.get(url)
                self.assertTemplateUsed(response, template)
