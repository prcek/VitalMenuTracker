from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging


# Create your models here.
class Account(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    balance = db.IntegerProperty()
    recount_date = db.DateTimeProperty('last recount') 
    last_change = db.DateTimeProperty('date changed')
    def __unicode__(self):
       return self.name


    def updateBalance(self):
        if self.balance is None:
            self.balance = 0
        else:
            self.balance = self.balance + 1
            self.recount_date = datetime.datetime.utcnow()


    def setChange(self):
        self.change_date = datetime.datetime.utcnow()


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
   
                 

