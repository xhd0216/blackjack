from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
# Create your views here.
from randomthoughts.drawing.tech_lib import get_image
import json


def get_symbol(req):
    """ main api """
    symbol = req.GET.get("s", None)
    gap = req.GET.get("g", None)
    rng = req.GET.get("r", None)
    fig = get_image()
    #raise ValueError("here %d" % len(fig))
    resp = HttpResponse(fig)
    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')