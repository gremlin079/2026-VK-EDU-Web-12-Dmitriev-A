from django.contrib import admin

from .models import (
    Question,
    Answer,
    Tag,
    QuestionLike,
    AnswerLike
)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

    raw_id_fields = ('author',)
    readonly_fields = ('created_at',)

    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'created_at'
    )

    search_fields = (
        'title',
        'text',
        'author__username'
    )

    list_filter = (
        'created_at',
        'tags'
    )

    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)

    readonly_fields = ('created_at',)

    list_select_related = ('author',)

    inlines = [AnswerInline]

    list_per_page = 50


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'question',
        'author',
        'created_at'
    )

    search_fields = (
        'text',
        'author__username'
    )

    list_filter = ('created_at',)

    raw_id_fields = ('question', 'author')

    list_select_related = ('question', 'author')

    readonly_fields = ('created_at',)


class HasQuestionsFilter(admin.SimpleListFilter):
    title = 'Наличие вопросов'
    parameter_name = 'has_questions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть вопросы'),
            ('no', 'Нет вопросов'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                questions__isnull=False
            ).distinct()

        if self.value() == 'no':
            return queryset.filter(
                questions__isnull=True
            )

        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = (HasQuestionsFilter,)
    list_per_page = 50


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'question__title')

    list_display = ('id', 'user', 'question', 'created_at')

    raw_id_fields = ('user', 'question')

    list_select_related = ('user', 'question')

    list_filter = ('created_at',)


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'answer__text')

    list_display = ('id', 'user', 'answer', 'created_at')

    raw_id_fields = ('user', 'answer')

    list_select_related = ('user', 'answer')

    list_filter = ('created_at',)