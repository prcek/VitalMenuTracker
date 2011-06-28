from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging


# Create your models here.
class Account(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    balance = db.IntegerProperty()
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


class Transaction(BaseModel):
    counterAccount = db.ReferenceProperty(Account)
    amount = db.IntegerProperty()
    create_date = db.DateTimeProperty() 
    desc = db.StringProperty(); 
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

