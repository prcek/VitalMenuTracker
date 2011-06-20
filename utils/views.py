# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django
import os
from google.appengine.api import users

from emails.models import EMailList
from utils.decorators import user_required, admin_required


def index(request):
    return redirect('/utils/email')

class EmailListForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea(attrs={'cols':160, 'rows':20}), required=False, label="Text s emaily")
    groupSize = forms.IntegerField(initial=20, label="Velikost skupiny")
    def getX(self):
        ie = self.cleaned_data['emails'] 
        ie = re.sub(r'[,;]'," ",ie)
        grs = self.cleaned_data['groupSize']
        oeSet = set([])
        for e in ie.split():
            if  re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e) != None:
                oeSet.add(e)

        oeList = sorted(oeSet)
        oe = "" 
        index = 0
        gr = 1
        for e in oeList:
            if index == 0:
                if gr != 1:
                    oe += '\n'
                oe += '%d: ' % gr
                gr+=1
                oe += e
            else:
                oe += ', '
                oe += e
            index+=1
            if (index % grs) == 0:
                index = 0
            

        return oe;



def emailFilter(request):
    if request.method == 'POST':
        form = EmailListForm(request.POST)
        if form.is_valid():
            result = form.getX()
    else:
        form = EmailListForm()
        result = ''
    return render_to_response('utils/emailFilter.html', { 'request':request, 'form': form , 'result': result})

@admin_required
def showEnv(request):
    env = os.environ
    env['DJANGO_VERSION'] = django.get_version()
    return render_to_response('utils/showEnv.html', { 'request':request, 'env':env })

def showHelp(request):
    return render_to_response('utils/showHelp.html', {  'request':request,  })

def showUser(request):
    info = "info about user:"
    base_uri = request.path
    user = users.get_current_user()
    admin = users.is_current_user_admin()
    nickname = ''
    email = ''
    user_id = ''

    auth = False
    if user:
        auth = True 
        nickname = user.nickname()
        email = user.email()
        user_id = user.user_id()
    return render_to_response('utils/showUser.html', { 'auth': auth,  'user_id': user_id, 'nickname': nickname, 'email':email, 'admin': admin, 'login_url':users.create_login_url(base_uri), 'logout_url': users.create_logout_url(base_uri), 'request':request,  })

