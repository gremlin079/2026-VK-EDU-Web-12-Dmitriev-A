from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Временные тестовые данные
QUESTIONS = [
    {
        'id': 35,
        'title': 'How to build a moon park?',
        'text': 'Guys, I have trouble with a moon park. Can anyone help me?',
        'avatar': 'DP',
        'votes': 5,
        'answers_count': 2,
        'tags': ['black-jack', 'bender'],
        'datetime': '2026-11-06T12:30',
        'time_ago': '2 часа назад',
        'answers': [
            {'author': 'Mr. Freeman', 'text': 'Start by planning the structure of your park.'},
            {'author': 'Dr. House', 'text': 'Consider the available space and resources.'},
        ],
    },
    {
        'id': 36,
        'title': 'Why does my CSS layout break?',
        'text': 'I am trying to align several elements using Flexbox.',
        'avatar': 'MF',
        'votes': 6,
        'answers_count': 2,
        'tags': ['css', 'flexbox'],
        'datetime': '2026-11-06T09:00',
        'time_ago': '5 часов назад',
        'answers': [
            {'author': 'Ben', 'text': 'Check the width of your flex items.'},
            {'author': 'Dr. Pepper', 'text': 'Try using flex-wrap.'},
        ],
    },
    {
        'id': 37,
        'title': 'How to center a block on a page?',
        'text': 'What is the easiest way to place an element in the center?',
        'avatar': 'DH',
        'votes': 2,
        'answers_count': 1,
        'tags': ['html', 'css'],
        'datetime': '2026-11-05T20:00',
        'time_ago': 'Вчера',
        'answers': [
            {'author': 'Mr. Freeman', 'text': 'You can use Flexbox with justify-content and align-items.'},
        ],
    },
    {
        'id': 38,
        'title': 'How does Python inheritance work?',
        'text': 'I want to understand inheritance in Python classes.',
        'avatar': 'AB',
        'votes': 9,
        'answers_count': 2,
        'tags': ['python', 'oop'],
        'datetime': '2026-11-05T18:00',
        'time_ago': 'Вчера',
        'answers': [
            {'author': 'Ben', 'text': 'A child class can inherit methods and attributes from a parent class.'},
            {'author': 'Dr. Pepper', 'text': 'Look at the class syntax and super().'},
        ],
    },
    {
        'id': 39,
        'title': 'What is the difference between Grid and Flexbox?',
        'text': 'When should I use CSS Grid instead of Flexbox?',
        'avatar': 'JK',
        'votes': 4,
        'answers_count': 1,
        'tags': ['css', 'flexbox'],
        'datetime': '2026-11-05T16:00',
        'time_ago': 'Вчера',
        'answers': [
            {'author': 'Dr. House', 'text': 'Grid is useful for two-dimensional layouts, Flexbox for one-dimensional layouts.'},
        ],
    },
    {
        'id': 40,
        'title': 'How to create a list in Python?',
        'text': 'I need to store several values in one variable.',
        'avatar': 'LM',
        'votes': 3,
        'answers_count': 1,
        'tags': ['python'],
        'datetime': '2026-11-05T14:00',
        'time_ago': 'Вчера',
        'answers': [
            {'author': 'Ben', 'text': 'Use square brackets, for example: numbers = [1, 2, 3].'},
        ],
    },
    {
        'id': 41,
        'title': 'How to connect a CSS file?',
        'text': 'My styles are not being applied to the HTML page.',
        'avatar': 'TS',
        'votes': 7,
        'answers_count': 1,
        'tags': ['html', 'css'],
        'datetime': '2026-11-04T12:00',
        'time_ago': '2 дня назад',
        'answers': [
            {'author': 'Mr. Freeman', 'text': 'Check the link tag and the path to your CSS file.'},
        ],
    },
    {
        'id': 42,
        'title': 'What is a Python dictionary?',
        'text': 'How can I store key-value pairs in Python?',
        'avatar': 'NP',
        'votes': 8,
        'answers_count': 1,
        'tags': ['python'],
        'datetime': '2026-11-04T10:00',
        'time_ago': '2 дня назад',
        'answers': [
            {'author': 'Dr. Pepper', 'text': 'Use curly brackets: {"name": "Alex"}. '},
        ],
    },
    {
        'id': 43,
        'title': 'Why do we need HTML semantics?',
        'text': 'What is the purpose of semantic HTML elements?',
        'avatar': 'AR',
        'votes': 1,
        'answers_count': 1,
        'tags': ['html'],
        'datetime': '2026-11-03T15:00',
        'time_ago': '3 дня назад',
        'answers': [
            {'author': 'Ben', 'text': 'Semantic elements make the structure clearer for browsers and developers.'},
        ],
    },
    {
        'id': 44,
        'title': 'How to write a Python function?',
        'text': 'I am learning functions and do not understand the syntax.',
        'avatar': 'MK',
        'votes': 5,
        'answers_count': 1,
        'tags': ['python'],
        'datetime': '2026-11-03T12:00',
        'time_ago': '3 дня назад',
        'answers': [
            {'author': 'Mr. Freeman', 'text': 'Use def followed by the function name and parentheses.'},
        ],
    },
    {
        'id': 45,
        'title': 'How does position: relative work?',
        'text': 'I do not understand how relative positioning changes an element.',
        'avatar': 'EV',
        'votes': 3,
        'answers_count': 1,
        'tags': ['css'],
        'datetime': '2026-11-02T12:00',
        'time_ago': '4 дня назад',
        'answers': [
            {'author': 'Dr. House', 'text': 'It positions the element relative to its normal position.'},
        ],
    },
    {
        'id': 46,
        'title': 'What is the DOM?',
        'text': 'Can someone explain the Document Object Model?',
        'avatar': 'SG',
        'votes': 10,
        'answers_count': 1,
        'tags': ['html', 'javascript'],
        'datetime': '2026-11-01T12:00',
        'time_ago': '5 дней назад',
        'answers': [
            {'author': 'Ben', 'text': 'The DOM represents an HTML document as a tree of objects.'},
        ],
    },
]


def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)

    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


def index(request):
    page_obj = paginate(QUESTIONS, request)

    return render(request, 'questions/index.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
    })


def hot(request):
    sorted_questions = sorted(
        QUESTIONS,
        key=lambda item: item['votes'],
        reverse=True
    )

    page_obj = paginate(sorted_questions, request)

    return render(request, 'questions/hot.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
    })


def tag(request, tag_name):
    filtered_questions = [
        item for item in QUESTIONS
        if tag_name.lower() in [tag.lower() for tag in item['tags']]
    ]

    page_obj = paginate(filtered_questions, request)

    return render(request, 'questions/tag.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'tag_name': tag_name,
    })


def detail(request, question_id):
    question_item = next(
        (item for item in QUESTIONS if item['id'] == question_id),
        None
    )

    if question_item is None:
        raise Http404('Вопрос не найден')

    return render(request, 'questions/question.html', {
        'question_item': question_item,
    })


def ask(request):
    return render(request, 'questions/ask.html')