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
    createConfig('REPORT_DAILY_SUMMARY','1')    
    createConfig('REPORT_DAILY_TRANSACTIONS','1')
    createConfig('PDF_TEST_TEXT',u'Příliš žluťoučký kůň úpěl ďábelské ódy (.CZ?!)')
    
