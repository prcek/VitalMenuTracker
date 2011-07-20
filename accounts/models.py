from appengine_django.models import BaseModel
from google.appengine.ext import db
#from vital.models import OrderItem
import datetime
import logging


# Create your models here.
class Account(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    balance = db.IntegerProperty()
    purpose = db.StringProperty(choices=['cash','credit','user','other']) 
    report_email = db.StringProperty()
    report_active = db.BooleanProperty()
    report_in_summary = db.BooleanProperty()
    recount_date = db.DateTimeProperty('last recount') 
    last_change = db.DateTimeProperty('date changed')
    def __unicode__(self):
       return self.name


    def setChange(self):
        self.change_date = datetime.datetime.utcnow()

    def getReportInfo(self):
        report = 'id: %d' % self.key().id()
        report = report +', name:'
        if self.name != None:
            report = report + ' "%s"' % self.name
        else:
            report = report + ' ?'
        
        report = report + ', balance: '
        if self.balance != None:
            report = report + '%d' % self.balance
        else:
            report = report + '?'

        if self.last_change != None:
            report = report + ', last change: %s' % self.last_change
        
        return report
    def as_csv_row(self):
        return [self.key().id(), name, desc, balance, report_email, report_active, report_in_summary, last_change]

    def as_select_string(self):
        return "[%d] %s - %s" % (self.key().id(), self.purpose, self.name)

class Transaction(BaseModel):
    counter_account_key = db.ReferenceProperty(collection_name='counter_account_key')
    order_item_key = db.ReferenceProperty(collection_name='order_item_key')
    clearance_item_key = db.ReferenceProperty(collection_name='clearance_item_key')
    amount = db.IntegerProperty()
    create_date = db.DateTimeProperty() 
    desc = db.StringProperty() 
    purpose = db.StringProperty(choices=['deposit','payment','transfer','correction']) 
    
    def setDate(self):
        self.create_date = datetime.datetime.utcnow()

    def trSave(self):
        a = Account.get(self.parent_key())
        if a.balance == None:
            a.balance = 0
        a.balance+=self.amount
        a.last_change = datetime.datetime.utcnow()
        a.save()
        return BaseModel.save(self)

    def save(self):
        return db.run_in_transaction(self.trSave)

        
    def getReportInfo(self):
        return '%d,%s;%d;"%s"' % (self.key().id(),self.create_date, self.amount, self.desc)

    def as_csv_row(self):
        return [self.key().id(), amount, create_date, desc,counterAccount]
