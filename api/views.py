from threading import Thread

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from api.models import UserAPIKey
from api.serializers import UserAPIKeySerializer
from api.utils import IsAPIKeyOwner, ParamRequired, Response, IsAdminKey, APITokenAuth
from search.scraping.requester import crawl


def methods(request):
    return render(request, 'docs/api_methods.html', context={})


def make_request(request):
    if request.method == 'POST':
        post = request.POST
        data = {
            post['var1']: post['var1_val'],
            post['var2']: post['var2_val'],
            post['var3']: post['var3_val'],
        }

        r = requests.post('https://khrmff.online/' + request.POST['url'], data={**data}, verify=False)
        try:
            return render(request, 'make_request.html', context={'resp': r.json()})
        except:
            return render(request, 'make_request.html', context={'resp': r.text})
    else:
        return render(request, 'make_request.html')


def quickstart(request):
    return render(request, 'docs/api_quickstart.html')


def objects(request):
    return render(request, 'docs/api_objects.html')


def errors(request):
    return render(request, 'docs/api_errors.html')


@login_required()
def create_key(request):
    if request.method == 'POST':
        if UserAPIKey.objects.get_usable_keys().filter(user=request.user).count() >= 5:
            return render(request, 'keys/max_key_amount.html')

        data = {'user': request.user.pk, 'name': request.POST.get('name'),
                'requests_per_minute': int(request.POST.get('requests_per_minute'))}

        serializer = UserAPIKeySerializer(data=data)
        if serializer.is_valid():
            key = serializer.save()
            return render(request, 'keys/key_created.html', context={'raw_api_key': key[1]})
        else:
            return render(request, 'keys/create_key.html', context={'errors': serializer.errors})

    elif request.method == 'GET':
        if UserAPIKey.objects.get_usable_keys().filter(user=request.user).count() >= 5:
            return render(request, 'keys/max_key_amount.html')
        return render(request, 'keys/create_key.html', context={})


def redirect_to_docs(request):
    return redirect('docs-index')


class DeactivateUserAPIKey(APIView):
    permission_classes = [IsAPIKeyOwner]
    serializer_class = UserAPIKeySerializer
    http_method_names = ['get', 'post', 'options']

    # TODO: here and in other serializers with .active, set queryset to .filter(active=True)
    queryset = UserAPIKey.objects.all()
    required_params = ['prefix']

    def options(self, request, *args, **kwargs):
        resp = HttpResponse()
        # ajax will never calm down so here i am writing VERY bad code,
        # probably a lot simpler solution exists. This works though
        resp['Access-Control-Allow-Credentials'] = 'true'
        resp['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
        resp["Access-Control-Allow-Headers"] = "Access-Control-Allow-Headers, access-control-allow-origin, Origin," \
                                               "Accept, X-Requested-With, " \
                                               "Content-Type, Access-Control-Request-Method, " \
                                               "Access-Control-Request-Headers "

        return resp

    def get(self, request):
        if request.method == 'POST':
            data = request.POST
        else:
            # GET method; elif request.method == 'GET':
            data = request.GET

        for i in self.required_params:
            if i not in data:
                raise ParamRequired('Parameter %s was required but wasn\'t specified' % i)

        apikey = get_object_or_404(self.queryset, prefix=data.get('prefix').rstrip().lstrip())
        self.check_object_permissions(request, apikey)

        apikey.deactivate()
        apikey.save()

        # TODO: exception on accessing Inactive data
        return Response({'active': self.serializer_class(apikey, context={'request': request}).data['revoked']})

    def post(self, request):
        return self.get(request)


class StartCrawling(APIView):
    permission_classes = [IsAdminKey]
    authentication_classes = [APITokenAuth]
    # aXyNizxG.KmS56UHBpVzPT0B4lrrhLt5dp6JnZYtJ
    serializer_class = UserAPIKeySerializer
    http_method_names = ['post']

    def post(self, request):
        data = request.POST
        if not data.get('start_page'):
            raise ParamRequired('Parameter start_page was required but wasn\'t specified')

        p = Thread(target=lambda: crawl(data['start_page']))
        p.start()
        return Response({'ok': True})

