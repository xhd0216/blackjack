import json
import os
import urllib3
import jwt

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseServerError, FileResponse


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



def get_image_full_path(file_path, file_id):
    if not file_path:
        file_path = os.environ['STATICIMGPATH']
    file_name = "%s.png" % file_id
    return os.path.join(file_path, file_name)


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

USER_NAME = os.environ['USERNAME']
DATAPLANE_NAME = os.environ['DATAPLANENAME']
with open('%s/%s.pem.sk' % (os.environ['PUBLICKEYPATH'], USER_NAME), 'r') as sk:
    SIGNING_KEY = sk.read()


# XXX: think how to load secret keys
def get_image_id(cfg):
    """ get image id """
    """
        get_tick_id is a multithreading task; it returns the image id if found
        if not found, it will return None and start a thread to finish the work
    """
    http = urllib3.PoolManager()
    payload = {
                'user': USER_NAME,
                'symbol': cfg['symbol'],
                'interval': cfg['interval'],
              }
    token = jwt.encode(payload, SIGNING_KEY, algorithm='RS256')
    resp = http.request('POST', '%s:5000/info' % DATAPLANE_NAME,
                        headers = {'token': token, 'user': USER_NAME})
    if resp.status != 200:
        return None
    ret = resp.data.decode()
    return json.loads(ret)


def get_symbol(req):
    """ main api """
    comp_cfg = {}
    for k in REQ_PARAM:
        if k in req.GET and req.GET[k] is not '':
            comp_cfg[REQ_PARAM[k]] = req.GET[k]

    try:
        # FIXME: get_image_id should have full config
        file_doc = get_image_id(comp_cfg)
        # TODO: check if the file is update-to-date
        if not file_doc:
            file_id = "NOT_READY"
        else:
            file_id = file_doc['_id']
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
