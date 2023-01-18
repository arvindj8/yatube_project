from http import HTTPStatus

from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

ALL_POSTS = 13
QUANTITY_POSTS_REMAINDER = 3


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='TestUser1',
                                            email='test@mail.ru',
                                            password='testPass123'),
            text='Test text one',
            group=Group.objects.create(title='test_group', slug='test-slug')
        )
        cls.post2 = Post.objects.create(
            author=User.objects.get(username='TestUser1'),
            text='Test text two',
            group=Group.objects.create(title='test_group_2', slug='test-slug_2')
        )

    def setUp(self):
        # Создаем автора поста
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def _assert_post_has_attrs(self, post, id, author, group):
        """Проверка отображения постов при передаче в context"""
        self.assertEqual(post.id, id)
        self.assertEqual(post.author, author)
        self.assertEqual(post.group, group)

    def _asset_check_form_true(self, response):
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
        неавторизованного пользователя и если при создании поста
        передается группа, этот пост появляется в index, group_list, profile"""
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
                self._assert_post_has_attrs(response.context.get('post'),
                                            self.post.id,
                                            self.post.author,
                                            self.post.group)

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
        """Проверка: пост не попал в группу, для которой не был предназначен."""
        response = self.author_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        get_object_post = response.context.get('post').group
        self.assertTrue(get_object_post, self.post2.group)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом выводит посты."""
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('title'),
                         'Последние обновления на сайте')
        first_object = response.context.get('post')
        self._assert_post_has_attrs(first_object, self.post.id,
                                    self.post.author, self.post.group)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        self._asset_check_form_true(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse
                                          ('posts:post_edit',
                                           kwargs={'post_id': self.post.id}))
        self._asset_check_form_true(response)


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

    def setUp(self):
        for post_temp in range(ALL_POSTS):
            Post.objects.create(
                text=f'text{post_temp}', author=self.author,
                group=self.group
            )

    def test_pages_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        templates = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.author}
            ),
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.AMOUNT_POSTS)

    def test_pages_contains_three_records(self):
        # Остаток постов на второй странице равно 3.
        templates = {
            'posts/index.html': reverse('posts:index') + '?page=2',
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2',
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.author}
            ) + '?page=2'
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 QUANTITY_POSTS_REMAINDER)
