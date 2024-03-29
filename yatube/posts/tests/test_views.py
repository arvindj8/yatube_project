import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

ADDITIONAL_POSTS = 3


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Готовим картинку
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        # Загружаем картинку
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user_author = User.objects.create_user(username='AuthorUser1')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Test text one',
            group=Group.objects.create(title='test_group',
                                       slug='test-slug'),
            image=uploaded)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        # Создаем автора поста
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def _assert_post_has_attrs(self, post, author, group, img):
        """Проверка отображения постов при передаче в context"""
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.author, author)
        self.assertEqual(post.group, group)
        self.assertEqual(post.image, img)

    def _assert_check_form_true(self, response):
        """Проверка, что форма на странице использует соответствующую форму"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_templates_posts_view_guest_user(self):
        """Тестируем что posts/view используют соответствующие шаблоны для
        анонимного пользователя"""
        templates = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.post.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_create_and_correct_show_post_group_list(self):
        """Тестируем что если при создании поста передается группа и картинка,
        этот пост появляется в group_list"""
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        first_post = response.context.get('post')
        self._assert_post_has_attrs(first_post,
                                    self.post.author,
                                    self.post.group,
                                    self.post.image)

    def test_create_and_correct_show_profile(self):
        """Тестируем что если при создании поста передается группа и картинка,
        этот пост появляется в profile"""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}
        ))
        first_post = response.context.get('post')
        self._assert_post_has_attrs(first_post,
                                    self.post.author,
                                    self.post.group,
                                    self.post.image)

    def test_create_and_correct_show_post_detail_list(self):
        """Тестируем что если при создании поста передается группа и картинка,
        этот пост появляется в post_detail"""
        response = self.client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_post = response.context.get('post')
        self._assert_post_has_attrs(first_post,
                                    self.post.author,
                                    self.post.group,
                                    self.post.image)

    def test_templates_posts_view_auth_user(self):
        """Тестируем posts/view используют соответствующие шаблоны auth user"""
        templates = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_create_and_show_post_group(self):
        """Проверка: пост не попал в группу, для которой не предназначен."""
        response = self.author_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        get_object_post = response.context.get('post').group
        self.assertTrue(get_object_post, self.post.group)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом выводит посты."""
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('title'),
                         'Последние обновления на сайте')
        first_post = response.context.get('post')
        self._assert_post_has_attrs(first_post,
                                    self.post.author,
                                    self.post.group,
                                    self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        self._assert_check_form_true(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse
                                          ('posts:post_edit',
                                           kwargs={'post_id': self.post.id}))
        self._assert_check_form_true(response)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_user = Client()
        cls.author = User.objects.create_user(username='TestUser2')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        cache.clear()

    def setUp(self):
        for post_temp in range(ADDITIONAL_POSTS + settings.AMOUNT_POSTS):
            Post.objects.bulk_create([Post(
                text=f'text{post_temp}',
                author=self.author,
                group=self.group)]
            )

    def _paginator_pages(self):
        templates_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author})
        ]
        return templates_paginator

    def test_pages_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        templates_paginator = self._paginator_pages()
        for reverse_name in templates_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.AMOUNT_POSTS)

    def test_pages_contains_three_records(self):
        """Проверка, что остаток постов на второй странице равно 3."""
        templates_paginator = self._paginator_pages()
        for reverse_name in templates_paginator:
            reverse_name += '?page=2'
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 ADDITIONAL_POSTS)


class IndexPageCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='AuthorUser1')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Test text one',
            group=Group.objects.create(title='test_group',
                                       slug='test-slug'))

    def setUp(self):
        self.client = Client()

    def test_main_page_cache(self):
        cache.clear()
        # Проверяем, что запись присутствует в содержимом ответа.
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, self.post.text)

        # Далее удаляем запись из базы данных
        self.post.delete()

        # Удаленная запись все еще присутствует в содержимом ответа
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, self.post.text)

        # Очищаем кэш
        cache.clear()

        # Проверяем, что удаленной записи больше нет в содержимом ответа
        response = self.client.get(reverse('posts:index'))
        self.assertNotContains(response, self.post.text)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Userfollow')
        cls.author = User.objects.create_user(username='Userisauthor')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Test text one',
            group=Group.objects.create(title='test_group',
                                       slug='test-slug'))

    def setUp(self):
        self.guest_user = Client()

        self.authorized_user = Client()
        self.authorized_user.force_login(user=self.user)

    def _create_following_author(self):
        """Создаем подписку на любимого автора"""
        self.authorized_user.get(reverse('posts:profile_follow',
                                         kwargs={'username': self.author}))

    def test_templates_follow_used(self):
        """Проверяем, что страница вывода постов любимых авторов
        использует соответствующий html шаблон"""
        response = self.authorized_user.get(reverse('posts:follow_index'))
        self.assertTemplateUsed(response, 'posts/follow.html')

    def test_add_following(self):
        """Тестируем, что пользователь может подписаться от любимого автора"""
        # Проверяем что пользователь не подписан на авторов
        quantity_following_one = Follow.objects.count()

        # Создаем подписку на любимого автора
        self._create_following_author()

        # Проверяем, что пользователь подписался на любимого автора
        quantity_following_second = Follow.objects.count()
        self.assertEqual(quantity_following_second, quantity_following_one + 1)
        # Проверяем, что запись в БД о любимом авторе появилась
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.author).exists())

    def test_delete_following(self):
        """Тестируем, что пользователь может отписаться от любимого автора"""
        # Создаем подписку на любимого автора
        quantity_following_one = Follow.objects.count()
        self.authorized_user.get(reverse('posts:profile_follow',
                                         kwargs={'username': self.author}))

        # Проверяем, что пользователь подписался на автора
        quantity_following_second = Follow.objects.count()

        # Создаем подписку на любимого автора
        self.authorized_user.get(reverse('posts:profile_unfollow',
                                         kwargs={'username': self.author}))
        quantity_following_three = Follow.objects.count()

        # Проверяем, что автор добавился в подписку
        self.assertEqual(quantity_following_second, quantity_following_one + 1)
        # Проверяем, что автор удалился из подписки
        self.assertEqual(quantity_following_three, quantity_following_one)

    def test_posts_correct_show_following(self):
        """Тестируем, что после подписки на любимого автора посты выводятся
        на главную страницу с любимыми постами follow.html"""
        response = self.authorized_user.get(reverse('posts:follow_index'))
        first_post_before_follow = response.context.get('post')

        # Создаем подписку на любимого автора
        self.authorized_user.get(reverse('posts:profile_follow',
                                         kwargs={'username': self.author}))

        response_after_follow = self.authorized_user.get(
            reverse('posts:follow_index'))
        first_post_after_follow = response_after_follow.context.get('post')

        # Проверяем, что до подписки посты не отображались в ленте
        self.assertIsNone(first_post_before_follow)
        # Проверяем, что после подписки посты отображаются в ленте
        self.assertEqual(first_post_after_follow, self.post)

    def test_add_following_only_one(self):
        """Тестируем, что пользователь может подписаться от любимого автора"""
        # Проверяем что пользователь не подписан на авторов
        quantity_following_one = Follow.objects.count()

        # Создаем подписку на любимого автора два раза
        self._create_following_author()
        self._create_following_author()
        self._create_following_author()

        quantity_following_second = Follow.objects.count()

        # Проверяем, что подписка создалась только один раз
        self.assertEqual(quantity_following_second, quantity_following_one + 1)

    def test_follow_redirect_anonymous_user(self):
        """Тестируем доступность страницы follow для анонимного пользователя"""
        response = self.guest_user.get(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
