# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django
import os
from google.appengine.api import users
from google.appengine.ext import blobstore

from emails.models import EMailList
from utils.models import User, Config
from utils.data import handle_uploaded_file, delete_uploaded_file, response_uploaded_file, decode_uploaded_file
from utils.decorators import user_required, power_required,  admin_required
from utils.config import getConfig

import logging


def index(request):
    return redirect('/utils/email')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ( 'active', 'name','email','power' )

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ( 'active', 'name','value' )

class UploadFileForm(forms.Form):
    post_action_ok = forms.CharField(widget=forms.widgets.HiddenInput())
    post_action_error = forms.CharField(widget=forms.widgets.HiddenInput())
    title = forms.CharField(max_length=50)
    file = forms.FileField()


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

@admin_required
def config_list(request):
    list = Config.objects.all().fetch(100)
    return render_to_response('utils/config_list.html', RequestContext(request, { 'config_list':list }))

@admin_required
def config_show(request,config_id):
    config = Config.get_by_id(int(config_id))
    if config is None:
        raise Http404
    return render_to_response('utils/config_show.html', RequestContext(request, { 'config': config }))

@admin_required
def config_create(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            config  = form.save(commit=False)
            config.save()
            logging.info('new config created - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            return redirect('/utils/config/')
    else:
        form = ConfigForm() 
    return render_to_response('utils/config_create.html', RequestContext(request, { 'form': form }))

@admin_required
def config_edit(request, config_id):
    config = Config.get_by_id(int(config_id))
    if config is None:
        raise Http404
    if request.method == 'POST':
        form = ConfigForm(request.POST, instance=config)
        if form.is_valid():
            logging.info('edit config before - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            form.save(commit=False)
            logging.info('edit config after - id: %s key: %s data: %s' % (config.key().id() , config.key(), config))
            config.save()
            return redirect('/utils/config/')
    else:
        form = ConfigForm(instance=config)
    return render_to_response('utils/config_edit.html', RequestContext(request, { 'form': form }) ) 

@admin_required
def pdf_test(request):
    from utils.pdf import pdftest
    from utils.config import getConfig
    pdf = pdftest(getConfig('PDF_TEST_TEXT'))
    r =  HttpResponse(pdf,mimetype='application/pdf')
    r['Content-Disposition'] = 'attachment; filename=pdf_test.pdf'
    return r

@admin_required
def csv_test(request):
    from utils.data import dump_to_csv
    import StringIO
    output = StringIO.StringIO()
    dump_to_csv(Config.objects.all(), output)
    r = HttpResponse(output.getvalue())
#    r =  HttpResponse(output.getvalue(),mimetype='text/comma-separated-values')
#    r['Content-Disposition'] = 'attachment; filename=csv_test.csv'
    return r

@admin_required
def csv_test_import(request, file_key):
    from utils.data import read_blob_csv
    objs = read_blob_csv(file_key,Config)
    logging.info(objs)
    return render_to_response('utils/config_show.html', RequestContext(request, { 'config': objs[1] }))
    #return HttpResponse('ok')



@admin_required
def files_list(request):
    list = blobstore.BlobInfo.all().order('-creation').fetch(100) 
    return render_to_response('utils/file_list.html', RequestContext(request, { 'file_list':list }))

@admin_required
def files_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logging.info('file upload - "%s"' % request.FILES['file']) 
            handle_uploaded_file(request.FILES['file'])
            return redirect('/utils/files/')
    else:
        form = UploadFileForm() 
    return render_to_response('utils/file_upload.html', RequestContext(request, { 'form': form }))

@admin_required
def files_upload_gae(request):
    form = UploadFileForm(initial={'post_action_ok':'/utils/files/upload_ok/', 'post_action_error':'/utils/files/upload_error/'}) 
    url = blobstore.create_upload_url('/upload')
    return render_to_response('utils/file_upload_gae.html', RequestContext(request, { 'form': form, 'target_url': url }))

@admin_required
def files_post_ok(request,file_key):
    return render_to_response('utils/file_post_upload.html', RequestContext(request, { 'result': 'ok' , 'key':file_key}))

@admin_required
def files_post_error(request,file_key):
    return render_to_response('utils/file_post_upload.html', RequestContext(request, { 'result': 'error', 'key':file_key }))


@admin_required
def files_get(request, file_key):
    logging.info('file get key = "%s"'%file_key)
    return response_uploaded_file(file_key)

@admin_required
def files_delete(request, file_key):
    logging.info('file delete key = "%s"'%file_key)
    delete_uploaded_file(file_key)
    return redirect('/utils/files')

@admin_required
def files_decode(request, file_key, coding):
    logging.info('file decode key:"%s" coding:"%s"' % (file_key, coding))
    new_key = decode_uploaded_file(file_key,coding)
    logging.info('result key: "%s"' % new_key)
    return HttpResponse('ok - key:%s'%new_key) 


@admin_required
def files_op(request, file_key):
    info = blobstore.BlobInfo.get(file_key)
    if info is None:
        raise Http404
    return render_to_response('utils/file_op.html', RequestContext(request, { 'info': info }))
    
@admin_required
def config_setup(request):
    from utils.config import setupConfig
    setupConfig()
    return HttpResponse("ok")

def captcha_test(request):
    from utils.captcha import displayhtml,submit
    last_result = '?'
    if request.method == 'POST':
        challenge = request.POST['recaptcha_challenge_field']
        response  = request.POST['recaptcha_response_field']
        remoteip  = os.environ['REMOTE_ADDR']
        logging.info("challenge=%s, response=%s, remoteip=%s"%(challenge,response,remoteip))
        resp = submit(challenge, response, getConfig('CAPTCHA_PRIVATE_KEY',''), remoteip)
        logging.info(resp)
        if resp.is_valid:
            logging.info('OK')
            last_result = 'OK'
        else:
            logging.info('ERROR')
            last_result = 'ERROR'

    html_captcha = displayhtml(getConfig('CAPTCHA_PUBLIC_KEY',''))
    return render_to_response('utils/captcha.html', RequestContext(request, { 'html_captcha': html_captcha , 'last_result':last_result}))


def debugTest(request):
    debug = '+ěščřžýáíé'
    from utils.pdf import pdftest
    pdftest()
    return HttpResponse(debug)



