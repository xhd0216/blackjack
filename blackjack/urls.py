from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("serve", views.serve_card, name="check_and_serve"),
    path("restart", views.start_new_game, name="start_a_new_game"),
]