# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins
from accounts.utils import getAccountsReport, getDetailAccountReport
from accounts.models import Account


import logging


def index(request):
    return render_to_response('reports/index.html', RequestContext(request))

@cron_required
def cron_test(request):
    logging.info('cron test')
#    send_mail_to_admins('test report','this is test report')
#    account_id = Account.objects.all().get().key().id()
#    account_report = 'detail ' + getDetailAccountReport(account_id)
#    logging.info('account report: "%s"' % account_report)
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))

@cron_required
def cron_daily(request):
    logging.info('cron daily')
    account_report = getAccountsReport()
    logging.info('accounts report: %s', account_report)
    send_mail_to_admins('VMTracker daily report',account_report)
    if request.cron_request:
        logging.info('HttpResponse ok')
        return HttpResponse('ok')
    return render_to_response('reports/cron.html', RequestContext(request))


