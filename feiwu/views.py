import json
import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError, FileResponse

from randomthoughts.drawing.tech_lib import get_image
from trendlines.server import drawing

html = """
<!DOCTYPE html>
<html>
<head>
    <title>picture</title>
</head>
<body>
    <img src="/random/figure" alt="haha">
</body>
</html>
"""

def generate_pic(req):
    """ download data and generate figure """
    file_path = os.environ['STATICIMGPATH']
    filename = drawing(None, file_path=file_path)
    try:
        resp = FileResponse(open(os.path.join(file_path, filename)))
    except Exception as e:
        return HttpResponseServerError("exception")
    return resp


def get_symbol(req):
    """ main api """
    symbol = req.GET.get("s", None)
    gap = req.GET.get("g", None)
    rng = req.GET.get("r", None)
    resp = HttpResponse(html)
    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')
