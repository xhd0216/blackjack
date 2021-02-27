from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from randomthoughts.stock_codes.download_prices import stock_download
import json

import plotly.graph_objects as go


def get_image(data):
    fig = go.Figure([go.Scatter(x=data["timestamp"], y=data["close"])])
    #fig = go.Figure([go.Scatter(x=data["timestamp"], y=data["close"]), go.Bar(x=data["timestamp"], y=data["volume"])])
    return fig.to_html(include_plotlyjs="cdn")


def index(req):
    data = stock_download("tsla", "1d", "1y")
    #raise ValueError("here")
    resp = HttpResponse(get_image(data))
    #resp = JsonResponse(data)

    return resp