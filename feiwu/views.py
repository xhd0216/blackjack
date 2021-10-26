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
    <img src="/random/figure?id=%s" alt="pic not found">
</body>
</html>
"""

def generate_pic(req):
    """ download data and generate figure """
    filename = req.GET.get("id", None)
    if filename:
        filename += '.png'
    file_path = os.environ['STATICIMGPATH']
    full_file_path = os.path.join(file_path, filename)
    try:
        resp = FileResponse(open(full_file_path, 'r'))
    except Exception as e:
        return HttpResponseServerError("exception", full_file_path, str(e))
    return resp


def get_symbol(req):
    """ main api """
    symbol = req.GET.get("s", None)
    gap = req.GET.get("g", None)
    rng = req.GET.get("r", None)
    try:
        file_path = os.environ['STATICIMGPATH']
        filename = drawing(None, file_path=file_path)
        file_id = filename.split('.')[0]
        referer = req.headers.get("X-FROM-TG", None)
        if referer:
            resp = HttpResponse(file_id)
        else:
            resp = HttpResponse(html % file_id)
    except Exception as e:
        return HttpResponseServerError("exception happened")

    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')
