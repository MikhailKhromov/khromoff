from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from search.models import Page


def index(request):
    if not request.user.is_superuser:
        # TODO: change this to BETATEST user rights.
        raise PermissionDenied

    return render(request, 'search.html')


@csrf_exempt
def search(request):
    query = request.GET.get('query')
    page = request.GET.get('page')
    if not page:
        page = 1
    if not query or len(query) == 1:
        redirect('search')

    result_pages = Page.objects.all()
    # magic here (finding by query and aligning)

    # result_pages = [{'url': 'https://google.com', 'desc': 'yes. it is google.'},
    #                 {'url': 'https://khrmff.ru', 'desc': 'my site.'}]
    for i in query.split():
        result_pages = result_pages.filter(searchword__word=i)

    # end magic
    return render(request, 'results.html', context={'pages': result_pages})


def settings(request):
    # start scraping...
    return render(request, 'settings.html')

