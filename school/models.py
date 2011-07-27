from appengine_django.models import BaseModel
from google.appengine.ext import db
import datetime
import logging


class Season(BaseModel):
    name = db.StringProperty()
    hidden = db.BooleanProperty(default=False) 
    actual = db.BooleanProperty(default=False)

class Category(BaseModel):
    name = db.StringProperty()
    
class Course(BaseModel):
    code = db.StringProperty()
    name = db.StringProperty()
    
class Group(BaseModel):
    name = db.StringProperty()
    order_key = db.IntegerProperty(default=None)
    invisible = db.BooleanProperty(default=True)

class Student(BaseModel):
    name = db.StringProperty()  
    
    
