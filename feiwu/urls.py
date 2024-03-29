from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("q", views.get_symbol, name="drawing"),
    path("figure", views.generate_pic, name="figure"),
]
