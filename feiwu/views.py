from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from random_thoughts.options_codes.download_prices import extract_data_wrapper
import json

import plotly.express as px

def get_image():
    fig =px.scatter(x=range(10), y=range(10))
    return fig.to_html(include_plotlyjs="cdn")

    

def index(req):
    _, data = extract_data_wrapper("aapl")
    #resp = HttpResponse(json.dumps(data, indent=4, sort_keys=True))
    resp = HttpResponse(get_image())
    return resp