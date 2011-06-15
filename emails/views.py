# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django

from emails.models import EMailList


def index(request):
    return redirect('/emails/groups/')

class EMailGroupForm(forms.Form):
    name = forms.CharField()
    desc = forms.CharField(required=False)
    emails = forms.CharField(widget=forms.Textarea(attrs={'cols':160, 'rows':20}), required=False, label="emaily")


def emailGroups(request):
    emaillists = EMailList.objects.all().fetch(10)
    return render_to_response('emails/emailGroups.html', { 'emaillists': emaillists, 'request':request })

def emailGroupShow(request, emailGroupId):
    el = EMailList.get_by_id(int(emailGroupId))
    if el  is None:
        raise Http404
    return render_to_response('emails/emailGroup.html', {'request':request,  'el': el})

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
    return render_to_response('emails/emailGroup.html', { 'request':request, 'form' : form})

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
 
    return render_to_response('emails/emailGroup.html', { 'form' : form, 'request':request })


