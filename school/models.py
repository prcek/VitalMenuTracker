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
    name = db.StringProperty(default='')
    print_line_1 = db.StringProperty(default='')
    print_line_2 = db.StringProperty(default='')
    group_mode = db.StringProperty(choices=['Flat','Group','Pair'], default='Flat')
    hidden = db.BooleanProperty(default=False) 
    @staticmethod
    def get_by_category_and_id(category,id):
        return Course.get(db.Key.from_path('Course',id, parent = category.key()))
    
class Group(BaseModel):
    name = db.StringProperty()
    mode = db.StringProperty(choices=['Flat','Group','Pair','Import'], default='Flat')
    order_key = db.IntegerProperty(default=None)
    invisible = db.BooleanProperty(default=True)
    @staticmethod
    def get_by_course_and_id(course,id):
        return Group.get(db.Key.from_path('Group',id, parent = course.key()))
 

class Student(BaseModel):
    name = db.StringProperty()  
    surname = db.StringProperty()
    sex = db.StringProperty(choices=['s','d','p'])
    payment = db.IntegerProperty()
    to_pay = db.IntegerProperty()
    payment_info = db.StringProperty()
    a_street = db.StringProperty()
    a_no = db.StringProperty()
    a_post_code = db.StringProperty()
    phone = db.StringProperty()
    email = db.StringProperty()
    spam = db.BooleanProperty()
    student = db.BooleanProperty()
    student_check = db.BooleanProperty()
    comment = db.StringProperty()
    year = db.IntegerProperty() 
    
    @staticmethod
    def get_by_group_and_id(group,id):
        return Student.get(db.Key.from_path('Student',id, parent = group.key()))
    
    
