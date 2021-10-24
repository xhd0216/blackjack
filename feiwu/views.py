import json
import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError
# Create your views here.
from randomthoughts.drawing.tech_lib import get_image
from trendlines.server import drawing

html = """
<!DOCTYPE html>
<html>
<head>
    <title>picture</title>
</head>
<body>
    <img src="/static/%s" alt="haha">
</body>
</html>
"""

def get_symbol(req):
    """ main api """
    symbol = req.GET.get("s", None)
    gap = req.GET.get("g", None)
    rng = req.GET.get("r", None)
    try:
      #fig = get_image(symbol, gap, rng)
      filename = drawing(None, file_path=os.environ['STATICIMGPATH'])
    except Exception as e:
      return HttpResponseServerError("found exception %s" % str(e))

    #resp = HttpResponse(fig)
    resp = HttpResponse(html % filename)
    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')
