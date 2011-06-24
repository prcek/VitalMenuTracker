# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required



import logging


def index(request):
    return render_to_response('reports/index.html', RequestContext(request))

@cron_required
def cron_test(request):
    logging.info('cron test')
    if request.cron_request:
        return HttpReponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))

@cron_required
def cron_daily(request):
    logging.info('cron daily')
    if request.cron_request:
        return HttpReponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))


