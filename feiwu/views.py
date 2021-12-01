import json
import os
import urllib3
import jwt

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError, FileResponse

from trendlines.server import drawing, get_image_full_path
from trendlines.web import get_tick_id


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
    full_file_path = get_image_full_path(None, filename)
    try:
        resp = FileResponse(open(full_file_path, 'r'))
    except Exception as e:
        return HttpResponseServerError("exception", full_file_path, str(e))
    return resp


REQ_PARAM = {
    "s": "symbol",
    "g": "interval",
    "r": "range",
}

def fetch_image(comp_cfg):
    try:
        file_path = os.environ['STATICIMGPATH']
        filename = drawing(None, file_path=file_path, comp_cfg=comp_cfg)
        file_id = filename.split('.')[0]
        return file_id
    except Exception as e:
        raise e


def get_image_id(cfg):
    """ get image id """
    """
        get_tick_id is a multithreading task; it returns the image id if found
        if not found, it will return None and start a thread to finish the work
    """
    #return get_tick_id(cfg)
    http = urllib3.PoolManager()
    payload = {
                'user': 'frontend',
                'symbol': cfg['symbol'],
                'interval': cfg['interval'],
              }
    token = jwt.encode(payload, sk, algorithm='RS256')
    resp = http.request('POST', 'data_interface_ctn:5000/info',
                        headers = {'token': token, 'user': 'test'})
    if resp.status != 200:
        return None
    ret = resp.data.decode()
    return json.loads(ret)['_id']


def get_symbol(req):
    """ main api """
    comp_cfg = {}
    for k in REQ_PARAM:
        if k in req.GET and req.GET[k] is not '':
            comp_cfg[REQ_PARAM[k]] = req.GET[k]

    try:
        # FIXME: get_image_id should have full config
        file_id = get_image_id(comp_cfg)
        if not file_id:
            file_id = "NOT_READY"
        referer = req.headers.get("X-FROM-TG", None)
        if referer:
            resp = HttpResponse(file_id)
        else:
            resp = HttpResponse(html % file_id)
    except Exception as e:
        resp = HttpResponseServerError("exception happened %s" % str(e))

    return resp

def index(req):
    return render(req, 'feiwu/homepage.html')
