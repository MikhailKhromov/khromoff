from django.urls import path

from . import views

urlpatterns = [
    path('search', views.index, name='search'),  # redirect
    path('results', views.search, name='search_results'),  # redirect
    path('settings', views.settings, name='search_settings'),  # redirect

]

handler404 = 'khromoff.views.error404'
handler500 = 'khromoff.views.error500'
