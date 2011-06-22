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
   

