# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
#from google.appengine.ext.db.djangoforms import forms
from django import forms
import re
import sys
import django
import logging
from email.utils import parseaddr
from emails.models import EMailList,EMailTemplate,EMailJob,EMailSubJob,EMailJobData
from vital.views import process_incoming_email_order
import files
from utils.data import get_blob_data
from google.appengine.api.mail import EmailMessage
from google.appengine.api import taskqueue
from utils.config import getConfig,getConfigBool,getConfigInt


 

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

    if getConfigBool("ENABLE_MAIL_TEST",False):
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
 


def incoming_email(request):
    logging.info(request.POST)
    filename= request.POST['filename']
    logging.info('processing incoming email %s'%filename)
    data = files.read_file(filename)

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

    if a_from == 'info@vitalmenu.cz':
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
            
            try:
                email = EmailMessage(et.data)
                email.sender = getConfig('DEFAULT_SENDER')
                email.to = to_a
                email.check_initialized()

                if getConfigBool("ENABLE_MAIL_TEST",False):
                    logging.info('sending...')
                    email.send()
                else:
                    logging.info('disabled')
        

            except:
                logging.info("can't init email! %s"%sys.exc_info()[1])
                return HttpResponse("can't init email - %s"%sys.exc_info()[1])


            return redirect('..')
    else:
        form = EMailAddressForm()
 
    return render_to_response('emails/email_template_test_send.html', RequestContext(request, { 'form' : form, 'et':et}))

class EMailJobCreateForm(forms.Form):
    email_group_id = forms.ChoiceField()
    email_template_id = forms.ChoiceField()
    def __init__(self, data = None, email_groups = [], email_templates = []):
        super(self.__class__,self).__init__(data)
        self.fields['email_group_id'].choices=[(g.key(),g.name) for g in email_groups]
        self.fields['email_template_id'].choices=[(t.key(),t.name) for t in email_templates]


def email_job(request):
    email_jobs = EMailJob.objects.all().fetch(100)
    return render_to_response('emails/email_jobs.html', RequestContext(request, { 'list': email_jobs}))

def email_job_show(request,job_id):
    job = EMailJob.get_by_id(int(job_id))
    if job is None:
        raise Http404
    sub_list = EMailSubJob.all().ancestor(job)
    job_data = EMailJobData.all().ancestor(job).get()
    return render_to_response('emails/email_job_show.html', RequestContext(request, { 'sub_list': sub_list, 'job':job, 'job_data':job_data}))

def email_job_prepare(request,job_id):
    job = EMailJob.get_by_id(int(job_id))
    if job is None:
        raise Http404
    logging.info('prepare mail job:%s'%job)
    if job.status != 'new':
        HttpResponse('ign')

    job_data = EMailJobData.all().ancestor(job).get()

    for i in range(0,len(job_data.emails),job_data.split_count):
        subjob = EMailSubJob(parent = job)
        subjob.emails_offset = i
        subjob.emails = job_data.emails[i:i+job_data.split_count]
        subjob.emails_count = len(subjob.emails)
        subjob.status = 'prepare'
        subjob.save()
        logging.info('subjob:%s'%subjob)

    
    job.status = 'prepare'
    job.save()
    return HttpResponse('ok')

def email_job_start(request,job_id):
    job = EMailJob.get_by_id(int(job_id))
    if job is None:
        raise Http404
    logging.info('starting mail job:%s'%job)
    if job.status != 'prepare':
        HttpResponse('ign')
   
    taskqueue.add(url='/tasks/start_email_job/%d/'%job.key().id(), method='GET')
 
    return redirect('..')

def email_job_start_task(request,job_id):
    job = EMailJob.get_by_id(int(job_id))
    if job is None:
        raise Http404
    logging.info('starting mail job:%s'%job)
    if job.status != 'prepare':
        HttpResponse('ign')
   
    sub_list = EMailSubJob.all().ancestor(job)
    for s in sub_list:
        logging.info('start: %s'%s)
        taskqueue.add(url='/tasks/fire_email_subjob/%s/'%s.key(), method='GET')

    logging.info('end')
    
 
    return HttpResponse('ok')

def fire_email_subjob(request,subjob_key):

    if not getConfigBool('ENABLE_MAIL_JOBS',False):
        logging.info('ENABLE_MAIL_JOBS != True, ignore') 
        return HttpResponse('disabled')
        


    sub_job = EMailSubJob.get(subjob_key)
    if sub_job is None:
        logging.info('no sub_job')
        raise Http404

    job = EMailJob.get(sub_job.parent_key())
    if job is None:
        logging.info('no job')
        raise Http404


    job_data = EMailJobData.all().ancestor(job).get()
    if job_data is None:
        logging.info('no job_data')
        raise Http404

    try:
        email = EmailMessage(job_data.data)
        email.sender = job_data.sender
        email.to = job_data.sender
        email.check_initialized()
    except:
        logging.info("can't init email! %s"%sys.exc_info()[1])
        sub_job.status = 'error'
        sub_job.status_info = "can't init email message - %s"%sys.exc_info()[1]
        sub_job.save()
        return HttpResponse('error')



    logging.info('processing mail sub job:%s'%sub_job)
    sub_job.status = 'send'
    sub_job.save()

    for e in sub_job.emails:
        logging.info('sending email to %s'%e)
        try:
            email.to = e
            email.send() 
            sub_job.emails_done.extend([e])
        except:
            logging.info("can't init email! %s"%sys.exc_info()[1])
            sub_job.emails_error.extend([e])

    sub_job.status = 'done'
    sub_job.save()
    logging.info('result:%s'%sub_job)
    
    return HttpResponse('ok')


def email_job_create(request):
    email_groups = EMailList.all()
    email_templates = EMailTemplate.all()


    if request.method == 'POST':
        form = EMailJobCreateForm(request.POST,email_groups=email_groups, email_templates=email_templates)
        if form.is_valid():
            logging.info('creating new job request')
            el = EMailList.get(form.cleaned_data['email_group_id'])
            if el is None:
                raise Http404
            et = EMailTemplate.get(form.cleaned_data['email_template_id'])
            if et is None:
                raise Http404

            job = EMailJob()
            job.name = "'%s' -> '%s'"%(et.name,el.name)
            job.save()

            job_data = EMailJobData(parent=job)             
            job_data.sender = getConfig('DEFAULT_SENDER')
            job_data.split_count = getConfigInt('MAIL_SPLIT_COUNT',10)
            job_data.emails = el.emails
            job_data.data =  et.data

            job_data.save()
            job.data_ref = job_data.key()
            job.save()

            logging.info('new job: %s'%job)

            taskqueue.add(url='/tasks/prepare_email_job/%d/'%job.key().id(), method='GET')

            return redirect('..')
    else:
        form = EMailJobCreateForm(email_groups=email_groups, email_templates=email_templates)

    return render_to_response('emails/email_job_create.html', RequestContext(request, { 'form': form}))



