from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime

# Create your models here.
class Account(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    balance = db.IntegerProperty()
    recount_date = db.DateTimeProperty('last recount') 
    change_date = db.DateTimeProperty('date changed')
    def __unicode__(self):
       return self.question


    def updateBalance(self):
        if self.balance is None:
            self.balance = 0
        else:
            self.balance = self.balance + 1
            self.recount_date = datetime.datetime.utcnow()


    def setChange(self):
        self.change_date = datetime.datetime.utcnow()
                 

