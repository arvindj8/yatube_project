from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Текст нового поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(to=Group,
                              verbose_name='Группа',
                              help_text='Группа, к которой будет относиться '
                                        'пост',
                              on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='posts')
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='posts/',
                              blank=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name='follower')

    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='following')
