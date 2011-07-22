# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django
import logging

from emails.models import EMailList


def index(request):
    return redirect('/emails/groups/')

class EMailGroupForm(forms.Form):
    name = forms.CharField()
    desc = forms.CharField(required=False)
    emails = forms.CharField(widget=forms.Textarea(attrs={'cols':160, 'rows':20}), required=False, label="emaily")


def emailGroups(request):
    emaillists = EMailList.objects.all().fetch(10)
    return render_to_response('emails/emailGroups.html', RequestContext(request, { 'emaillists': emaillists}))

def emailGroupShow(request, emailGroupId):
    el = EMailList.get_by_id(int(emailGroupId))
    if el  is None:
        raise Http404
    return render_to_response('emails/emailGroup.html', RequestContext(request, { 'el': el}))

def emailGroupEdit(request, emailGroupId):
    el = EMailList.get_by_id(int(emailGroupId))
    if el  is None:
        raise Http404
    
    if request.method == 'POST':
        form = EMailGroupForm(request.POST)
        if form.is_valid():
            el.name = form.cleaned_data['name']
            el.desc = form.cleaned_data['desc']
            el.emailsFromString(form.cleaned_data['emails'])
            el.save()
            return redirect('../..')
    else:
        data = {'name':el.name, 'desc':el.desc, 'emails':el.emailsAsString()}
        form = EMailGroupForm(data)
    return render_to_response('emails/emailGroup.html', RequestContext(request, { 'form' : form}))

def emailGroupCreate(request):
    if request.method == 'POST':
        form = EMailGroupForm(request.POST)
        if form.is_valid():
            el = EMailList()
            el.name = form.cleaned_data['name']
            el.desc = form.cleaned_data['desc']
            el.emailsFromString(form.cleaned_data['emails'])
            el.save()
            return redirect('..')
    else:
        form = EMailGroupForm()
 
    return render_to_response('emails/emailGroup.html', RequestContext(request, { 'form' : form }))


def parse_email(request, file_key):
    from utils.data import get_blob_data
    from google.appengine.api.mail import EmailMessage
    from utils.config import getConfig

    data = get_blob_data(file_key)
    if data is None:
        raise Http404

    r = ""
    email = EmailMessage(data)
    email.check_initialized()
    email.sender = getConfig("MAIL_TEST_FROM")
    email.to = getConfig("MAIL_TEST_TO")

    if getConfig("MAIL_TEST",0) == "1":
        logging.info('sending email....')
        email.send()

    r = email.to_mime_message()

    return HttpResponse('parse ok - %s'%r)

def incoming_email(request, file_key):
    logging.info('processing incoming email %s'%file_key)

    return HttpResponse("ok") 
