import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testuser333')
        cls.auth_user = User.objects.create_user(username='authclient')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text one3',
            group=Group.objects.create(title='Заголовок для тестовой группы',
                                       slug='test_slug3',
                                       description='Тестовое описание3')
        )
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека для управления файлами и директориями:
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)
        # Создаём авторизованный клиент-автор
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def _create_new_post(self, text, reverse_url, img=None):
        """Создает пост с разными данными"""
        if img is None:
            form_data = {
                'text': text,
                'group': self.post.group.id,
            }
        else:
            form_data = {
                'text': text,
                'group': self.post.group.id,
                'image': img
            }

        response = self.author_client.post(
            reverse_url,
            data=form_data,
            follow=True
        )
        return response

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Проверка сколько постов до создания
        tasks_count = Post.objects.count()

        # Создаем пост
        text = self.post.text
        reverse_create = reverse('posts:post_create')
        response_create = self._create_new_post(text, reverse_create)

        self.assertRedirects(response_create, reverse('posts:profile', kwargs={
            'username': self.post.author}))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.post.author,
            text=self.post.text,
            group=self.post.group).exists())

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        # Create post
        text = self.post.text
        reverse_create = reverse('posts:post_create')
        response_create = self._create_new_post(text, reverse_create)
        get_post_text = response_create.context.get('post').text

        # Edit post
        new_text = 'New Text'
        reverse_edit = reverse('posts:post_edit',
                               kwargs={'post_id': self.post.id})
        response_edit = self._create_new_post(new_text, reverse_edit)
        get_edit_post_text = response_edit.context.get('post').text

        self.assertRedirects(
            response_edit, reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id}))
        self.assertTrue(get_edit_post_text, get_post_text)

    def test(self):
        """Тестируем, при отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных."""
        # Проверка сколько постов до создания
        posts_count = Post.objects.count()

        # Генерируем картинку
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

        # Создаем пост через post запрос
        reverse_create = reverse('posts:post_create')
        response_create = self._create_new_post(self.post.text,
                                                reverse_create, uploaded)

        self.assertRedirects(response_create, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.post.author,
            text=self.post.text,
            group=self.post.group,
            image='posts/small.gif').exists())
