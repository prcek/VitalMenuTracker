# -*- coding: utf-8 -*-
from utils.models import Config

def getConfig(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        return c.value
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
    createConfig('MAIL_TEST_TO','user@domain.com') 
    createConfig('MAIL_TEST_FROM','admin@domain.com') 
    createConfig('MAIL_TEST','0') 
    
