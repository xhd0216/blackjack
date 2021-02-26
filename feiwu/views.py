from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from random_thoughts.options_codes.download_prices import extract_data_wrapper
import json

def index(req):
    _, data = extract_data_wrapper("aapl")
    resp = HttpResponse(json.dumps(data, indent=4, sort_keys=True))
    return resp