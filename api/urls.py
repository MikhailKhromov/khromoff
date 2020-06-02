from django.urls import path, include

from . import views

urlpatterns = [
    path('docs/quickstart', views.quickstart, name='docs-index'),
    path('', views.redirect_to_docs),

    path('docs/methods', views.methods, name='docs-methods'),
    path('docs/objects', views.objects, name='docs-objects'),
    path('docs/errors', views.errors, name='docs-errors'),
    path('new-key', views.create_key, name='create-api-key'),

    # TODO: do it
    # path('docs/test-request', views.make_request, name='api-make-request'),

    path('method/', include('urlshortner.api.urls')),
    path('method/search.scrape', views.StartCrawling.as_view(), name='search-scrape'),
    path('method/apikey.deactivate', views.DeactivateUserAPIKey.as_view(), name='apikey-deactivate'),

]
