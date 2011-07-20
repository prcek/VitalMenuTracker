from appengine_django.models import BaseModel
from google.appengine.ext import db
from accounts.models import Account,Transaction
import datetime
import logging


# Create your models here.
class OrderGroup(BaseModel):
    active = db.BooleanProperty()
    date = db.DateProperty()
   

class Order(BaseModel):
    create_date = db.DateTimeProperty()
    csv_file_id = db.StringProperty()
    extra = db.BooleanProperty()

    def set_info(self,blob_info):
        self.create_date = blob_info.creation
        self.csv_file_id = blob_info.key().__str__()


class OrderItem(BaseModel):
    date = db.DateProperty()
    name = db.StringProperty()
    cost = db.IntegerProperty()
    undo_request = db.BooleanProperty(default=False)
    deleted = db.BooleanProperty(default=False)
    extra = db.BooleanProperty(default=False)
    owner_name = db.StringProperty()
    owner_surname = db.StringProperty()
    clearance_item_ref = db.ReferenceProperty(default=None)
    

#csv format - [count, date(dd.mm.yyyy), name, cost, name, surname]
    def from_csv_row(self,row=[]):
        d = row[1].split('.')
        self.date = datetime.date(int(d[2]),int(d[1]),int(d[0]))
        self.name = row[2]
        self.cost = int(row[3])
        self.owner_name = row[4]
        self.owner_surname = row[5]
        if (int(row[0])<0):
            self.undo_request = True
        else:
            self.undo_request = False 
         
        return True
    def __unicode__(self):
        if self.is_saved():
            return '[%s] %s %s %d' % (self.key().id(),self.date,self.name,self.cost)
        else:
            return '%s %s %d' % (self.date,self.name,self.cost)
    def as_select_string(self):
        return '[%s] %s %s %d' % (self.key().id(),self.date,self.name,self.cost)
         


class Clearance(BaseModel):
    date = db.DateProperty()        
    desc = db.StringProperty()
    clear = db.BooleanProperty(default=False)
    lock = db.BooleanProperty(default=False)
    status = db.StringProperty(choices=['new','clearing','closed','error'], default='new')

class ClearanceItem(BaseModel):
    purpose = db.StringProperty(choices=['pick','give','deposit','load'])
    clear = db.BooleanProperty(default=False) 
    account = db.ReferenceProperty(Account)
    transaction_item = db.ReferenceProperty(Transaction)
    order_item = db.ReferenceProperty(OrderItem)
    cost = db.IntegerProperty()
    desc = db.StringProperty()

    def as_select_string(self):
        return '[%s] %s %d %s' % (self.key().id(),self.purpose,self.cost,self.desc)
    
     
    
