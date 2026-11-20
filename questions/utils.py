from django.core.paginator import Paginator


def paginate(objects, request, per_page=5):
    paginator = Paginator(objects, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    page_obj.elided_page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    return page_obj