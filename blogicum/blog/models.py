from django.db import models
from django.contrib.auth import get_user_model

from .constants import LENGHT_CHARACTER_FIELDS, LIMIT_OUTPUT_STRING
from core.models import IsPublishedCreatedAt, CreatedAt

User = get_user_model()


class Location(IsPublishedCreatedAt):
    name = models.CharField('Название места',
                            max_length=LENGHT_CHARACTER_FIELDS)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:LIMIT_OUTPUT_STRING]


class Category(IsPublishedCreatedAt):
    title = models.CharField('Заголовок', max_length=LENGHT_CHARACTER_FIELDS)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:LIMIT_OUTPUT_STRING]


class Post(IsPublishedCreatedAt):
    title = models.CharField('Заголовок', max_length=LENGHT_CHARACTER_FIELDS)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    image = models.ImageField('Фото', upload_to='blog_image', blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:LIMIT_OUTPUT_STRING]


class Comment(CreatedAt):
    text = models.TextField('Комментарий',
                            max_length=LENGHT_CHARACTER_FIELDS)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:LIMIT_OUTPUT_STRING]
