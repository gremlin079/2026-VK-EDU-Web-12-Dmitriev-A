from django.db import models
from django.conf import settings
from django.db.models import (
    Count,
    OuterRef,
    Subquery,
    IntegerField,
    Value,
    F,
)
from django.db.models.functions import Coalesce

class ProfileManager(models.Manager):

    def best_members(self, limit=5):
        from questions.models import QuestionLike, AnswerLike

        question_likes = (
            QuestionLike.objects
            .filter(question__author_id=OuterRef('user_id'))
            .order_by()
            .values('question__author_id')
            .annotate(total=Count('id'))
            .values('total')[:1]
        )

        answer_likes = (
            AnswerLike.objects
            .filter(answer__author_id=OuterRef('user_id'))
            .order_by()
            .values('answer__author_id')
            .annotate(total=Count('id'))
            .values('total')[:1]
        )

        return (
            self.get_queryset()
            .select_related('user')
            .annotate(
                question_likes=Coalesce(
                    Subquery(
                        question_likes,
                        output_field=IntegerField()
                    ),
                    Value(0),
                    output_field=IntegerField()
                ),
                answer_likes=Coalesce(
                    Subquery(
                        answer_likes,
                        output_field=IntegerField()
                    ),
                    Value(0),
                    output_field=IntegerField()
                )
            )
            .annotate(
                total_likes=(
                    F('question_likes') + F('answer_likes')
                )
            )
            .filter(total_likes__gt=0)
            .order_by('-total_likes', 'user__username')[:limit]
        )


class Profile(models.Model):
    objects = ProfileManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )

    avatar = models.URLField(
        blank=True,
        verbose_name='Ссылка на аватар'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль: {self.user.username}'