from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging


# Create your models here.
class OrderGroup(BaseModel):
    active = db.BooleanProperty()
    date = db.DateProperty()
   

class Order(BaseModel):
    create_date = db.DateTimeProperty()
    csv_file_id = db.StringProperty()

    def set_info(self,blob_info):
        self.create_date = blob_info.creation
        self.csv_file_id = blob_info.key().__str__()


class OrderItem(BaseModel):
    date = db.DateProperty()
    name = db.StringProperty()
    cost = db.IntegerProperty()
    owner_name = db.StringProperty()
    owner_surname = db.StringProperty()

#csv format - [count, date(dd.mm.yyyy), name, cost, name, surname]
    def from_csv_row(self,row=[]):
        d = row[1].split('.')
        self.date = datetime.date(int(d[2]),int(d[1]),int(d[0]))
        self.name = row[2]
        self.cost = int(row[3])
        self.owner_name = row[4]
        self.owner_surname = row[5]
        return True
      