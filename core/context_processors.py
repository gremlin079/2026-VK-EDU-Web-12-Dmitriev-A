from questions.models import Tag
from core.models import Profile


def sidebar_data(request):
    return {
        'popular_tags': Tag.objects.popular(),
        'best_members': Profile.objects.best_members(),
    }
