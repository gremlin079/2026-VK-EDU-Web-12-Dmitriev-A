from django import forms
from django.utils.text import slugify

from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label='Теги',
        help_text='Укажите теги через запятую.',
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: Python, Django, HTML',
        })
    )

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags')
        labels = {
            'title': 'Заголовок вопроса',
            'text': 'Текст вопроса',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Кратко сформулируйте вопрос',
            }),
            'text': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Подробно опишите свою проблему...',
            }),
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')

        result = []
        used_names = set()

        for raw_name in raw_tags.split(','):
            name = raw_name.strip()

            if not name:
                continue

            if len(name) > 64:
                raise forms.ValidationError(
                    'Название каждого тега должно быть не длиннее 64 символов.'
                )

            normalized_name = name.casefold()

            if normalized_name not in used_names:
                result.append(name)
                used_names.add(normalized_name)

        return result

    def _get_or_create_tag(self, name):
        tag = Tag.objects.filter(name__iexact=name).first()

        if tag:
            return tag

        base_slug = slugify(name) or 'tag'
        base_slug = base_slug[:80]

        slug = base_slug
        counter = 2

        while Tag.objects.filter(slug=slug).exists():
            suffix = f'-{counter}'
            slug = f'{base_slug[:80 - len(suffix)]}{suffix}'
            counter += 1

        return Tag.objects.create(
            name=name,
            slug=slug
        )

    def _save_m2m(self):
        tag_names = self.cleaned_data.get('tags', [])

        tags = [
            self._get_or_create_tag(name)
            for name in tag_names
        ]

        self.instance.tags.set(tags)

    def save(self, commit=True, *, author):
        question = super().save(commit=False)
        question.author = author

        if commit:
            question.save()
            self.save_m2m()

        return question


class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('text',)
        labels = {
            'text': 'Ваш ответ',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Напишите свой ответ...',
            }),
        }

    def save(self, commit=True, *, author, question):
        answer = super().save(commit=False)

        answer.author = author
        answer.question = question

        if commit:
            answer.save()

        return answer