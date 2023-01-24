from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User
from users.forms import CreationForm


class TestsUsersForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm

    def setUp(self):
        self.guest_user = Client()

    def test_creation_user_form(self):
        """ТестируемБ что при заполнении формы users:signup
        создаётся новый пользователь."""
        check_user_data_base = User.objects.count()

        form_data = {
            'first_name': 'Testuser',
            'last_name': 'Pupkin',
            'username': 'testuser1',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'email': 'test@yandex.ru'
        }
        # Создаем пользователя
        self.client.post(reverse('users:signup'),
                         data=form_data,
                         follow=True)
        self.assertEqual(User.objects.count(), check_user_data_base + 1)
        self.assertTrue(User.objects.filter(username=form_data['username']))
