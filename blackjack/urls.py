from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("shuffle", views.serve_card, name="shuffle_serve"),
]