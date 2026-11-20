from django.shortcuts import render, get_object_or_404

from .models import Question, Tag
from .utils import paginate


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


def detail(request, question_id):
    question_item = get_object_or_404(
        Question.objects.with_related(), pk=question_id
    )
    answers_page = paginate(
        question_item.answers.with_related(), request, per_page=10
    )
    return render(request, 'questions/question.html', {
        'question_item': question_item,
        'answers': answers_page.object_list,
        'answers_page_obj': answers_page,
    })


def ask(request):
    return render(request, 'questions/ask.html')