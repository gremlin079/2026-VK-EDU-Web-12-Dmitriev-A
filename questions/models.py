from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import (
    Count,
    OuterRef,
    Subquery,
    IntegerField,
    Value,
)
from django.db.models.functions import Coalesce


class TagManager(models.Manager):

    def popular(self, limit=5):
        return (
            self.get_queryset()
            .annotate(
                questions_count=Count('questions', distinct=True)
            )
            .filter(questions_count__gt=0)
            .order_by('-questions_count', 'name')[:limit]
        )


class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Название'
    )

    slug = models.SlugField(
        max_length=80,
        unique=True,
        verbose_name='URL'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class QuestionManager(models.Manager):

    def with_related(self):

        likes = (
            QuestionLike.objects
            .filter(question_id=OuterRef('pk'))
            .order_by()
            .values('question_id')
            .annotate(total=Count('id'))
            .values('total')[:1]
        )

        answers = (
            Answer.objects
            .filter(question_id=OuterRef('pk'))
            .order_by()
            .values('question_id')
            .annotate(total=Count('id'))
            .values('total')[:1]
        )

        return (
            self.get_queryset()
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
            .annotate(
                likes_count=Coalesce(
                    Subquery(likes, output_field=IntegerField()),
                    Value(0),
                    output_field=IntegerField()
                ),
                answers_count=Coalesce(
                    Subquery(answers, output_field=IntegerField()),
                    Value(0),
                    output_field=IntegerField()
                )
            )
        )

    def new(self):
        return self.with_related().order_by('-created_at', '-id')

    def best(self):
        return self.with_related().order_by(
            '-likes_count',
            '-created_at'
        )

    def by_tag(self, slug):
        return (
            self.with_related()
            .filter(tags__slug=slug)
            .distinct()
        )


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Автор'
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )

    text = models.TextField(
        verbose_name='Текст вопроса'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='questions',
        blank=True,
        verbose_name='Теги'
    )

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'question',
            kwargs={'question_id': self.pk}
        )

    @property
    def votes(self):
        if hasattr(self, 'likes_count'):
            return self.likes_count
        return self.likes.count()

    @property
    def avatar(self):
        name = self.author.get_full_name() or self.author.username
        parts = name.split()
        return ''.join(part[0] for part in parts[:2]).upper()

    @property
    def datetime(self):
        return self.created_at.isoformat()

    @property
    def time_ago(self):
        return self.created_at.strftime('%d.%m.%Y %H:%M')


class AnswerManager(models.Manager):

    def with_related(self):
        return (
            self.get_queryset()
            .select_related('author', 'author__profile')
            .annotate(
                likes_count=Count('likes', distinct=True)
            )
            .order_by('created_at', 'id')
        )


class Answer(models.Model):
    objects = AnswerManager()

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Автор'
    )

    text = models.TextField(
        verbose_name='Текст ответа'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['created_at']

    def __str__(self):
        return f'Ответ #{self.pk} на вопрос #{self.question_id}'


class QuestionLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Пользователь'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Вопрос'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ('user', 'question')

    def __str__(self):
        return f'{self.user} → {self.question}'


class AnswerLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Пользователь'
    )

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Ответ'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user} → {self.answer}'
