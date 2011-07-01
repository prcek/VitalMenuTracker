from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging


# Create your models here.
class User(BaseModel):
    active = db.BooleanProperty()
    name = db.StringProperty()
    email = db.StringProperty()
    power = db.BooleanProperty()
    def __unicode__(self):
       return self.email


class Config(BaseModel):
    active = db.BooleanProperty()
    name = db.StringProperty()
    value = db.StringProperty()
    def as_csv_row(self):
        return [self.key().kind(),self.key().id(),self.active,self.name,self.value]
    def from_csv_row(self,row=[]):
        self.name = row[2]
        return True
        

