# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from google.appengine.api import taskqueue

import logging


def index(request):
    return render_to_response('school/index.html', RequestContext(request))

