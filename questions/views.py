from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect

from .models import Question, Tag
from .forms import QuestionForm, AnswerForm
from .utils import paginate


ANSWERS_PER_PAGE = 10


def index(request):
    page_obj = paginate(Question.objects.new(), request)

    return render(request, 'questions/index.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
    })


def hot(request):
    page_obj = paginate(Question.objects.best(), request)

    return render(request, 'questions/hot.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
    })


def tag(request, tag_name):
    current_tag = get_object_or_404(Tag, slug=tag_name)
    page_obj = paginate(Question.objects.by_tag(tag_name), request)

    return render(request, 'questions/tag.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'tag_name': current_tag.name,
    })


def _render_question_detail(request, question_item, answer_form=None):
    answers_page = paginate(
        question_item.answers.with_related(),
        request,
        per_page=ANSWERS_PER_PAGE
    )

    if answer_form is None:
        answer_form = AnswerForm()

    return render(request, 'questions/question.html', {
        'question_item': question_item,
        'answers': answers_page.object_list,
        'answers_page_obj': answers_page,
        'answer_form': answer_form,
    })


def detail(request, question_id):
    question_item = get_object_or_404(
        Question.objects.with_related(),
        pk=question_id
    )

    return _render_question_detail(request, question_item)


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)

        if form.is_valid():
            question = form.save(author=request.user)
            return redirect(question.get_absolute_url())

    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {
        'form': form,
    })


@login_required
@require_POST
def create_answer(request, question_id):
    question_item = get_object_or_404(
        Question,
        pk=question_id
    )

    form = AnswerForm(request.POST)

    if form.is_valid():
        answer = form.save(
            author=request.user,
            question=question_item
        )

        # Определяем страницу, на которой находится новый ответ.
        answers_count = question_item.answers.count()

        page_number = (
            (answers_count - 1) // ANSWERS_PER_PAGE
        ) + 1

        return redirect(
            f'{question_item.get_absolute_url()}'
            f'?page={page_number}#answer-{answer.pk}'
        )

    # Если форма заполнена неправильно, показываем ошибки
    # и сохраняем введённый пользователем текст.
    return _render_question_detail(
        request,
        question_item,
        answer_form=form
    )