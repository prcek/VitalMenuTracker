
from utils.config import getConfig
from google.appengine.api import mail
import logging


def send_mail_to_admins(subject='',message=''):
    logging.info('sending mail to admin') 
    sender = getConfig('ADMIN_EMAIL')
    if not sender:
        logging.info('missing admin email address (cfg key: ADMIN_EMAIL)')
        return

    if not mail.is_email_valid(sender):
        logging.info('admin email is not valid')


    #mail.send_mail(admin,admin,subject,message)
    mail.send_mail_to_admins(sender, subject,message)
        
    return

def send_mail_to_user(subject='',message='', user=None):
    logging.info('sending mail to user') 
    sender = getConfig('ADMIN_EMAIL')
    if not sender:
        logging.info('missing admin email address (cfg key: ADMIN_EMAIL)')
        return

    if not mail.is_email_valid(sender):
        logging.info('admin email is not valid')
        return

    if not user:
        logging.info('missing recipient email address')
        return

    if not mail.is_email_valid(user):
        logging.info('recipient email is not valid')
        return

    mail.send_mail(sender, user, subject,message)
        
    return
