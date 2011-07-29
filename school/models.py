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
    hidden = db.BooleanProperty(default=False) 

    @staticmethod
    def get_by_season_and_id(season, id):
        return Category.get(db.Key.from_path('Category',id, parent = season.key()))
    
class Course(BaseModel):
    code = db.StringProperty()
    name = db.StringProperty()
    hidden = db.BooleanProperty(default=False) 
    @staticmethod
    def get_by_category_and_id(category,id):
        return Course.get(db.Key.from_path('Course',id, parent = category.key()))
    
class Group(BaseModel):
    name = db.StringProperty()
    order_key = db.IntegerProperty(default=None)
    invisible = db.BooleanProperty(default=True)
    @staticmethod
    def get_by_course_and_id(course,id):
        return Group.get(db.Key.from_path('Group',id, parent = course.key()))
 

class Student(BaseModel):
    name = db.StringProperty()  
    @staticmethod
    def get_by_group_and_id(group,id):
        return Student.get(db.Key.from_path('Student',id, parent = group.key()))
    
    
