from django.urls import path

from .views import future_universites_privees, aide_view


urlpatterns = [
    path(
        'universites-privees-future/',
        future_universites_privees,
        name='universites_privees_future',
    ),
    path(
        'aide/',
        aide_view,
        name='aide',
    ),
]


