from django.http import HttpResponseRedirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from google.appengine.api import users
from utils.models import User
import logging

   
class AuthInfo:
    auth = False
    wrong = False
    admin = False
    power = False
    def __init__(self, request):
        self.gae_user = users.get_current_user()
        self.gae_admin = users.is_current_user_admin()
        if self.gae_user:
            self.user = User.objects.all().filter('email =',self.gae_user.email()).get()
        else:
            self.user = None

        self.login_url =  users.create_login_url(request.path) 
        self.logout_url =  users.create_logout_url(request.path) 

        if self.gae_admin:
            logging.info('auth: gae admin')
            self.auth = True
            self.admin = True
            self.name = self.gae_user.nickname()
            self.email = self.gae_user.email()
        else:
            if self.user and self.user.active:
                logging.info('auth: internal user')
                self.auth = True
                self.power = self.user.power
                self.name = self.user.name
                self.email = self.user.email
            else:
                if self.gae_user:
                    self.wrong = True
        
     

class Auth(object):
  def process_request(self, request):
    request.__class__.auth_info = AuthInfo(request)
    if not request.auth_info.auth:
        logging.info('unauthorised access')
        if request.auth_info.wrong:
            logging.info('wrong user')
            return render_to_response('relogin.html', RequestContext(request, { }))
            
        return HttpResponseRedirect(request.auth_info.login_url)
    return None
