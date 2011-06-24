from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden


from google.appengine.api import users
import logging


def user_required(function):
    def login_required_wrapper(request, *args, **kw):
        logging.info('user_required wrapper')
        if request.auth_info.auth:
            return function(request, *args, **kw)
        return HttpResponseRedirect(request.auth_info.login_url)
    return login_required_wrapper


def power_required(function):
    def login_required_wrapper(request, *args, **kw):
        logging.info('power_required wrapper')
        if request.auth_info.auth:
            if request.auth_info.power:
                return function(request, *args, **kw)
            else:
                return HttpResponseForbidden('power user required')
        return HttpResponseRedirect(users.create_login_url(request.path))
    return login_required_wrapper

def cron_required(function):
    def login_required_wrapper(request, *args, **kw):
        logging.info('cron_required wrapper')
        if request.auth_info.auth:
            if request.auth_info.admin or request.auth_info.cron:
                return function(request, *args, **kw)
            else:
                return HttpResponseForbidden('cron/admin user required')
        return HttpResponseRedirect(users.create_login_url(request.path))
    return login_required_wrapper

def admin_required(function):
    def login_required_wrapper(request, *args, **kw):
        logging.info('admin_required wrapper')
        if request.auth_info.auth:
            if request.auth_info.admin:
                return function(request, *args, **kw)
            else:
                return HttpResponseForbidden('admin user required')
        return HttpResponseRedirect(users.create_login_url(request.path))
    return login_required_wrapper
