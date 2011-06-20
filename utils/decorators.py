from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden


from google.appengine.api import users
import logging


def user_required(function):
    def login_required_wrapper(request, *args, **kw):
        user = users.get_current_user()
        if user:
            return function(request, *args, **kw)
        return HttpResponseRedirect(users.create_login_url(request.path))
    return login_required_wrapper

def admin_required(function):
    def login_required_wrapper(request, *args, **kw):
        user = users.get_current_user()
        if user: 
            if users.is_current_user_admin():
                return function(request, *args, **kw)
            else:
                return HttpResponseForbidden('admin required')
        return HttpResponseRedirect(users.create_login_url(request.path))
    return login_required_wrapper
