from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from randomthoughts.drawing.tech_lib import get_image
import json


def index(req):
    fig = get_image()
    resp = HttpResponse(fig)

    return resp