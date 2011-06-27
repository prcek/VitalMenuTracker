from accounts.models import Account,Transaction
import logging
import datetime

def getAccountsReport(user_id=None):
    if user_id:
        logging.info('generating report for user_id = %d ' % user_id)
    else:
        logging.info('generating overall report')

    report = 'accounts report %s\n' % (datetime.datetime.utcnow())
    report = report + '==================================================\n'

    
    account_list = Account.objects.all().fetch(100)    
    for account in account_list:
        report = report +  account.getReportInfo() + '\n'
         
    return report 

def getDetailAccountReport(account_id=None):
    if not account_id:
        return 'no account id'
   
    report = 'account detail report (account_id: %d, time: %s)\n' % (account_id, datetime.datetime.utcnow())

    account = Account.get_by_id(int(account_id))
    if account is None:
        report = report + 'account id:%d not found' % account_id
        return report

    report = report + '\nAccount:\n'
    report = report + account.getReportInfo()
    report = report + '\n\nLast 10 transactions:\n'

    transaction_list = Transaction.objects.all().ancestor(account).order('-create_date').fetch(10)
    for transaction in transaction_list:
        report = report + transaction.getReportInfo() + '\n'

    return report
    
