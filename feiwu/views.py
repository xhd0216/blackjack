from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError
# Create your views here.
from randomthoughts.drawing.tech_lib import get_image
import json


def get_symbol(req):
    """ main api """
    symbol = req.GET.get("s", None)
    gap = req.GET.get("g", None)
    rng = req.GET.get("r", None)
    try:
      fig = get_image(symbol, gap, rng)
    except:
      return HttpResponseServerError("Cannot find data for %s" % symbol)
      
    resp = HttpResponse(fig)
    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')
