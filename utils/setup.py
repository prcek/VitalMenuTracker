from django.http import HttpResponse, Http404
from utils.config import setupConfig
import os
def setup(request):
    env = os.environ
    dev = env['SERVER_SOFTWARE']
    if dev is None:
        return HttpResponse('no env[SERVER_SOFTWARE]')
    if not dev.startswith('Development'):
        return HttpResponse('no development mode')

    setupConfig()

    return HttpResponse('setup ok') 
