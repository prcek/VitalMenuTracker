# -*- coding: utf-8 -*-
from utils.models import Config
import logging

def getConfig(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        return c.value
    return dv 

def getConfigBool(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        logging.info('Config: %s=%s'%(name,c.value))
        if c.value=='1':
            return True
        else:
            return False
    
    return dv

def getConfigInt(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        logging.info('Config: %s=%s'%(name,c.value))
        try:
            return int(c.value)
        except:
            logging.info('Config: no Integer value!')
            return dv
    
    return dv
        

def createConfig(name,value):
    if getConfig(name) is None:
        c = Config()
        c.name = name
        c.value = value
        c.active = True
        c.save()

def setupConfig():
    createConfig('REPORT_DAILY_SUMMARY','0')    
    createConfig('REPORT_DAILY_TRANSACTIONS','0')
    createConfig('PDF_TEST_TEXT',u'Příliš žluťoučký kůň úpěl ďábelské ódy (.CZ?!)')
    createConfig('CLEARANCE_ALL_ORDER_ITEMS','0')
    createConfig('ADMIN_EMAIL','admin@domain.com') 
    createConfig('DEFAULT_SENDER','sender@domain.com')
    createConfig('MAIL_SPLIT_COUNT','10')
    createConfig('MAIL_TEST_TO','user@domain.com') 
    createConfig('MAIL_TEST_FROM','admin@domain.com') 
    createConfig('MAIL_TEST','0') 
    createConfig('ENABLE_MAIL_JOBS','0')
    createConfig('ENABLE_MAIL_TEST','0')
    createConfig('CAPTCHA_PUBLIC_KEY','1234567890')
    createConfig('CAPTCHA_PRIVATE_KEY','1234567890')
    
