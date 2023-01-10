from django.core.paginator import Paginator


def pagination(request, object_list, amount_obj):
    paginator = Paginator(object_list, amount_obj)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
