import random
import uuid

from faker import Faker

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from core.models import Profile
from questions.models import (
    Question,
    Answer,
    Tag,
    QuestionLike,
    AnswerLike,
)


BATCH_SIZE = 2000


class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            nargs='?',
            type=int,
            default=100,
            help='Коэффициент заполнения базы данных'
        )

    def handle(self, *args, **options):
        ratio = options['ratio']

        if ratio < 2:
            raise CommandError(
                'Минимальный ratio — 2: необходимо обеспечить '
                'достаточное количество уникальных лайков.'
            )

        self.fake = Faker('en_US')
        self.random = random.Random()
        self.prefix = uuid.uuid4().hex[:10]

        user_count = ratio
        question_count = ratio * 10
        answer_count = ratio * 100
        tag_count = ratio
        total_likes = ratio * 200

        self.stdout.write(
            self.style.SUCCESS(
                f'Начинаем заполнение БД. Ratio: {ratio}'
            )
        )

        # 1. Создание пользователей
        self.stdout.write('Создание пользователей...')

        user_ids = self.create_users(user_count)

        # 2. Создание профилей
        self.stdout.write('Создание профилей...')

        self.create_profiles(user_ids)

        # 3. Создание тегов
        self.stdout.write('Создание тегов...')

        tag_ids = self.create_tags(tag_count)

        # 4. Создание вопросов
        self.stdout.write('Создание вопросов...')

        question_ids = self.create_questions(
            question_count,
            user_ids
        )

        # 5. Связывание вопросов с тегами
        self.stdout.write('Связывание вопросов с тегами...')

        self.create_question_tags(question_ids, tag_ids)

        # 6. Создание ответов
        self.stdout.write('Создание ответов...')

        answer_ids = self.create_answers(
            answer_count,
            question_ids,
            user_ids
        )

        # 7. Создание лайков
        self.stdout.write('Создание лайков...')

        # Распределяем лайки между вопросами и ответами.
        # При этом соблюдаем ограничение уникальности.
        question_likes_count = min(
            total_likes // 2,
            len(user_ids) * len(question_ids)
        )

        answer_likes_count = total_likes - question_likes_count

        if answer_likes_count > len(user_ids) * len(answer_ids):
            raise CommandError(
                'Недостаточно уникальных сочетаний '
                'пользователей и ответов для создания лайков.'
            )

        self.create_likes(
            QuestionLike,
            'question_id',
            question_ids,
            question_likes_count,
            user_ids
        )

        self.create_likes(
            AnswerLike,
            'answer_id',
            answer_ids,
            answer_likes_count,
            user_ids
        )

        self.stdout.write(
            self.style.SUCCESS(
                '\nЗаполнение завершено!\n'
                f'Пользователи: {user_count}\n'
                f'Профили: {user_count}\n'
                f'Вопросы: {question_count}\n'
                f'Ответы: {answer_count}\n'
                f'Теги: {tag_count}\n'
                f'Лайки вопросов: {question_likes_count}\n'
                f'Лайки ответов: {answer_likes_count}\n'
                f'Всего лайков: {total_likes}'
            )
        )

    def create_users(self, count):
        ids = []
        password = make_password('AskAnswer123!')

        for start in range(0, count, BATCH_SIZE):
            batch_count = min(BATCH_SIZE, count - start)

            users = [
                User(
                    username=f'user_{self.prefix}_{i}',
                    email=self.fake.email(),
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    password=password,
                )
                for i in range(start, start + batch_count)
            ]

            created = User.objects.bulk_create(
                users,
                batch_size=BATCH_SIZE
            )

            ids.extend(user.pk for user in created)

        return ids

    def create_profiles(self, user_ids):
        profiles = [
            Profile(
                user_id=user_id,
                avatar=f'https://i.pravatar.cc/150?img={i % 70 + 1}'
            )
            for i, user_id in enumerate(user_ids)
        ]

        Profile.objects.bulk_create(
            profiles,
            batch_size=BATCH_SIZE
        )

    def create_tags(self, count):
        ids = []

        for start in range(0, count, BATCH_SIZE):
            batch_count = min(BATCH_SIZE, count - start)

            tags = [
                Tag(
                    name=f'{self.fake.word().capitalize()} {self.prefix}-{i}',
                    slug=f'tag-{self.prefix}-{i}'
                )
                for i in range(start, start + batch_count)
            ]

            created = Tag.objects.bulk_create(
                tags,
                batch_size=BATCH_SIZE
            )

            ids.extend(tag.pk for tag in created)

        return ids

    def create_questions(self, count, user_ids):
        ids = []

        for start in range(0, count, BATCH_SIZE):
            batch_count = min(BATCH_SIZE, count - start)

            questions = [
                Question(
                    author_id=self.random.choice(user_ids),
                    title=self.fake.sentence(nb_words=7),
                    text=self.fake.paragraph(nb_sentences=4),
                )
                for _ in range(batch_count)
            ]

            created = Question.objects.bulk_create(
                questions,
                batch_size=BATCH_SIZE
            )

            ids.extend(question.pk for question in created)

        return ids

    def create_question_tags(self, question_ids, tag_ids):
        through = Question.tags.through

        relations = []

        for i, question_id in enumerate(question_ids):
            first_tag = tag_ids[i % len(tag_ids)]

            relations.append(
                through(
                    question_id=question_id,
                    tag_id=first_tag
                )
            )

            if len(tag_ids) > 1:
                second_tag = tag_ids[(i + 1) % len(tag_ids)]

                relations.append(
                    through(
                        question_id=question_id,
                        tag_id=second_tag
                    )
                )

            if len(relations) >= BATCH_SIZE:
                through.objects.bulk_create(
                    relations,
                    batch_size=BATCH_SIZE
                )
                relations = []

        if relations:
            through.objects.bulk_create(
                relations,
                batch_size=BATCH_SIZE
            )

    def create_answers(self, count, question_ids, user_ids):
        ids = []

        for start in range(0, count, BATCH_SIZE):
            batch_count = min(BATCH_SIZE, count - start)

            answers = [
                Answer(
                    question_id=self.random.choice(question_ids),
                    author_id=self.random.choice(user_ids),
                    text=self.fake.paragraph(nb_sentences=3),
                )
                for _ in range(batch_count)
            ]

            created = Answer.objects.bulk_create(
                answers,
                batch_size=BATCH_SIZE
            )

            ids.extend(answer.pk for answer in created)

        return ids

    def create_likes(
            self,
            model,
            relation_field,
            object_ids,
            count,
            user_ids
    ):
        import math

        user_count = len(user_ids)
        object_count = len(object_ids)

        stride = user_count + 1

        while math.gcd(stride, object_count) != 1:
            stride += 1

        for start in range(0, count, BATCH_SIZE):
            batch_count = min(BATCH_SIZE, count - start)

            likes = []

            for i in range(start, start + batch_count):
                user_index = i % user_count
                cycle = i // user_count

                object_index = (
                                       user_index + cycle * stride
                               ) % object_count

                likes.append(
                    model(
                        user_id=user_ids[user_index],
                        **{
                            relation_field: object_ids[object_index]
                        }
                    )
                )

            model.objects.bulk_create(
                likes,
                batch_size=BATCH_SIZE
            )