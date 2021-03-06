# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from accounts.utils import getAccountsReport, getDetailAccountReport
from accounts.models import Account
#from google.appengine.ext import deferred
from google.appengine.api import taskqueue



import logging


def index(request):
    return render_to_response('reports/index.html', RequestContext(request))

def task_one_trans_report(request,account_id=None):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    logging.info('do_one_trans_report(%s)' % (account_id))
    account_report = getDetailAccountReport(account.key().id())
    logging.info('account report: "%s"' % account_report)
    send_mail_to_user('VMTracker account id:%d report' % int(account_id), account_report, account.report_email)
    return HttpResponse('ok')

def task_accounts_report(request):
    account_report = getAccountsReport()
    logging.info('accounts report: %s', account_report)
    send_mail_to_admins('VMTracker daily report',account_report)
    return HttpResponse('ok')
 
   
def do_trans_reports():
    account_list = Account.objects.all().fetch(100)
    for account in account_list:
        if account.report_active: 
            account_id = account.key().id()
            account_email = account.report_email
            logging.info('add task for "do_one_trans_report(%d,"%s")"' % (account_id, account_email))
            taskqueue.add(url='/tasks/mail_transaction_report/%s/'%account_id, method='GET')
            #deferred.defer(deferred_one_trans_report, account_id, account_email)
        else:
            logging.info('transaction report for account %d is disabled' % account.key().id())
    logging.info('all tasks planned')

def do_accounts_report():
    taskqueue.add(url='/tasks/mail_accounts_report/', method='GET')
#    deferred.defer(deferred_accounts_report)
        

@cron_required
def cron_test(request):
    logging.info('cron test')
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))

@cron_required
def cron_daily(request):
    logging.info('cron daily')

    if getConfig('REPORT_DAILY_SUMMARY'):
        do_accounts_report()
    else:
        logging.info('daily summary report disabled (cfg key: REPORT_DAILY_SUMMARY)')

    if getConfig('REPORT_DAILY_TRANSACTIONS'):
        do_trans_reports()
    else:
        logging.info('daily transactions report disabled (cfg key: REPORT_DAILY_TRANSACTIONS)')
        
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))


