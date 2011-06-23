# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django
import os
from google.appengine.api import users

from emails.models import EMailList
from utils.models import User
from utils.decorators import user_required, admin_required

import logging

def index(request):
    return redirect('/utils/email')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ( 'active', 'name','email','power' )



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
    return render_to_response('utils/emailFilter.html', RequestContext(request, { 'form': form , 'result': result}))

@admin_required
def showEnv(request):
    env = os.environ
    env['DJANGO_VERSION'] = django.get_version()
    return render_to_response('utils/showEnv.html', RequestContext(request, { 'env':env }))

def showHelp(request):
    return render_to_response('utils/showHelp.html', RequestContext(request, {   }))

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
    return render_to_response('utils/showUser.html', RequestContext(request, { 'auth': auth,  'user_id': user_id, 'nickname': nickname, 'email':email, 'admin': admin, 'login_url':users.create_login_url(base_uri), 'logout_url': users.create_logout_url(base_uri), }))


@admin_required
def user_list(request):
    list = User.objects.all().fetch(100)
    return render_to_response('utils/user_list.html', RequestContext(request, { 'user_list':list }))

@admin_required
def user_show(request,user_id):
    user = User.get_by_id(int(user_id))
    if user is None:
        raise Http404
    return render_to_response('utils/user_show.html', RequestContext(request, { 'user': user }))

@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            user  = form.save(commit=False)
            user.save()
            logging.info('new user created - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            return redirect('/utils/users/')
    else:
        form = UserForm() 
    return render_to_response('utils/user_create.html', RequestContext(request, { 'form': form }))

@admin_required
def user_edit(request, user_id):
    user = User.get_by_id(int(user_id))
    if user is None:
        raise Http404
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            logging.info('edit user before - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            form.save(commit=False)
            logging.info('edit user after - id: %s key: %s data: %s' % (user.key().id() , user.key(), user))
            user.save()
            return redirect('/utils/users/')
    else:
        form = UserForm(instance=user)
    return render_to_response('utils/user_edit.html', RequestContext(request, { 'form': form }) ) 


def debugTest(request):
    if request.auth:
        debug = 'auth ok'
    else:
        debug = 'neni'
    return HttpResponse(debug)
