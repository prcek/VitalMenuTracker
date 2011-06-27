# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins
from accounts.utils import getAccountsReport, getDetailAccountReport
from accounts.models import Account
from google.appengine.ext import deferred


import logging


def index(request):
    return render_to_response('reports/index.html', RequestContext(request))

def deferred_one_trans_report(account_id=None, account_email=None):
    logging.info('do_one_trans_report(%d,"%s")' % (account_id,account_email))
    account_report = 'detail ' + getDetailAccountReport(account_id)
    logging.info('account report: "%s"' % account_report)
    send_mail_to_admins('VMTracker account id:%d report' % account_id, account_report)

def deferred_accounts_report():
    account_report = getAccountsReport()
    logging.info('accounts report: %s', account_report)
    send_mail_to_admins('VMTracker daily report',account_report)
 
   
def do_trans_reports():
    account_list = Account.objects.all().fetch(100)
    for account in account_list:
        account_id = account.key().id()
        account_email = '' # account.owner_email
        logging.info('add task for "do_one_trans_report(%d,"%s")"' % (account_id, account_email))
        deferred.defer(deferred_one_trans_report, account_id, account_email)
    logging.info('all tasks planned')

def do_accounts_report():
    deferred.defer(deferred_accounts_report)
        

@cron_required
def cron_test(request):
    logging.info('cron test')
#    send_mail_to_admins('test report','this is test report')
#    account_id = Account.objects.all().get().key().id()
#    account_report = 'detail ' + getDetailAccountReport(account_id)
#    logging.info('account report: "%s"' % account_report)
#    do_trans_reports()
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))

@cron_required
def cron_daily(request):
    logging.info('cron daily')
    do_accounts_report()
    do_trans_reports()
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))


