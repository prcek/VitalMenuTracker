from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader


import logging


def index(request):
    return render_to_response('vital/index.html', RequestContext(request, { }))


def register_csv_order(request, file_key):
    return render_to_response('vital/register_csv_order.html', RequestContext(request, { 'file_key': file_key }))
