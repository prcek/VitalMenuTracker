# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import django
import logging
from email.utils import parseaddr
from emails.models import EMailList,EMailTemplate
from vital.views import process_incoming_email_order

from utils.data import get_blob_data
from google.appengine.api.mail import EmailMessage
from utils.config import getConfig


 

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

#http://code.google.com/p/googleappengine/issues/detail?id=2383
def fix_encoding(message):
    from google.appengine.api.mail import EncodedPayload
    if hasattr(message, 'body'):
        
        if isinstance(message.body, EncodedPayload):
            logging.info(message.body.encoding)
            if message.body.encoding == '8bit':
                message.body.payload = u'xxx' #message.body.payload.decode('utf-8')
                message.body.encoding = 'utf-8' 
                logging.info('Body encoding fixed')
    
    if hasattr(message, 'html'):    
        
        if isinstance(message.html, EncodedPayload):
            logging.info(message.html.encoding)    
            if message.html.encoding == '8bit':
                message.html.encoding = 'utf-8' 
                logging.info('HTML encoding fixed')
    if hasattr(message, 'attachments'):
        for file_name, data in _attachment_sequence(message.attachments):
            if isinstance(data, EncodedPayload):
                logging.info(data.encoding)
                if data.encoding == '8bit':
                    data.encoding = 'utf-8'
                    logging.info('Attachment encoding fixed')
    return message


def parse_email(request, file_key):
    data = get_blob_data(file_key)
    if data is None:
        raise Http404

    r = ""
    email = EmailMessage(data)
#    fix_encoding(email)     
    email.check_initialized()
    email.sender = getConfig("MAIL_TEST_FROM")
    email.to = getConfig("MAIL_TEST_TO")

    if getConfig("MAIL_TEST",0) == "1":
        logging.info('sending email....')
        email.send()

    r = email.to_mime_message()

    return HttpResponse('parse ok - %s'%r)

def process_incoming_email_template(template_id, data):
    logging.info('processing incoming email template')
    et = EMailTemplate.get_by_id(int(template_id))
    if et is None:
        logging.info('template not found')
        return

    if not et.open_for_import:
        logging.info('template is not open')
        return

    et.data = data
    et.open_for_import = False

    et.save()

    logging.info('template updated and closed')
 


def incoming_email(request, file_key):
    logging.info('processing incoming email %s'%file_key)

    data = get_blob_data(file_key)
    if data is None:
        raise Http404

    logging.info('email fetch ok')
    email = EmailMessage(data)
    a_to = parseaddr(email.to)[1]
    a_from = parseaddr(email.sender)[1]
    logging.info('email.to=%s'%a_to) 
    logging.info('email.sender=%s'%a_from) 

    if re.match(r'^import-order@',a_to):
        logging.info('import order')
        process_incoming_email_order(email)
        return HttpResponse("ok - import order")
    r = re.match(r'^import-email-(\d+)@',a_to) 
    if r:
        logging.info('import email, id %s'%r.group(1))
        process_incoming_email_template(r.group(1),data)
        return HttpResponse("ok - import email")
        

    return HttpResponse("ok -ign") 


class EMailTemplateForm(forms.ModelForm):
    class Meta:
        model = EMailTemplate
        fields = ( 'name', 'open_for_import' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data


def email_template(request):
    email_templates = EMailTemplate.objects.all().fetch(100)
    return render_to_response('emails/email_templates.html', RequestContext(request, { 'list': email_templates}))

def email_template_show(request, template_id):
    et = EMailTemplate.get_by_id(int(template_id))
    if et is None:
        raise Http404
    return render_to_response('emails/email_template_show.html', RequestContext(request, { 'et': et}))


def email_template_create(request):
    if request.method == 'POST':
        form = EMailTemplateForm(request.POST)
        if form.is_valid():
            et = EMailTemplate()
            et.name = form.cleaned_data['name']
            et.open_for_import = form.cleaned_data['open_for_import']
            et.save()
            logging.info('new email template: %s'%et)
            return redirect('..')
    else:
        form = EMailTemplateForm()
 
    return render_to_response('emails/email_template_create.html', RequestContext(request, { 'form' : form }))

def email_template_edit(request, template_id):
    et = EMailTemplate.get_by_id(int(template_id))
    if et  is None:
        raise Http404
    
    if request.method == 'POST':
        form = EMailTemplateForm(request.POST)
        if form.is_valid():
            et.name = form.cleaned_data['name']
            et.open_for_import = form.cleaned_data['open_for_import']
            et.save()
            return redirect('../..')
    else:
        form = EMailTemplateForm(instance=et)
    return render_to_response('emails/email_template_edit.html', RequestContext(request, { 'form' : form}))


class EMailAddressForm(forms.Form):
    address = forms.EmailField(required=True)

 
def email_template_test_send(request, template_id):
    et = EMailTemplate.get_by_id(int(template_id))
    if et  is None:
        raise Http404

    if request.method == 'POST':
        form = EMailAddressForm(request.POST)
        if form.is_valid():
            to_a = form.cleaned_data['address']
            logging.info('test send template id %d, to: %s', et.key().id(), to_a)
            #TODO 
            return redirect('..')
    else:
        form = EMailAddressForm()
 
    return render_to_response('emails/email_template_test_send.html', RequestContext(request, { 'form' : form, 'et':et}))


def email_job(request):
    pass

def email_job_show(request,job_id):
    pass

def email_job_create(request):
    pass



