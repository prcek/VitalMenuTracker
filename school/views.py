# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from google.appengine.api import taskqueue
from google.appengine.ext import db
from school.models import Season,Category,Course,Group,Student

import logging


def index(request):

    logging.info('test of long key chain')
   
    season = Season.objects.all().get()
    if season is None:
        season = Season()
        season.name = '2011/12'
        season.save()
    
    logging.info('season=%s'%season)

    category = Category.objects.all().get()
    if category is None:
        category = Category(parent = season)
        category.name = 'cat1'
        category.save()
    
    logging.info('category=%s'%category)

    course = Course.objects.all().get()
    if course is None:
        course = Course(parent = category)
        course.code = 'X1'
        course.save()
   
    logging.info('course=%s'%course) 

    group = Group.objects.all().get()
    if group is None:
        group = Group(parent = course)
        group.name = 'gr1'
        group.save()

    logging.info('group=%s'%group)

    student = Student.objects.all().get()
    if student is None:
        student = Student(parent = group)
        student.name ='st1'
        student.save()

    logging.info('student=%s'%student)


    st = Student.objects.all().ancestor(course).get()

    logging.info('ancestor test:%s'%st)

    return render_to_response('school/index.html', RequestContext(request))

def test_index(request):
    action = request.GET.get('action','index')
    logging.info('action = %s'%action)
    if action == 'index':
        pass
    elif action == 'setup':
        season_1 = Season()
        season_1.name = "2011/12"
        season_1.save()
        season_2 = Season()
        season_2.name = "2012/13"
        season_2.save()

        cat_1 = Category(parent = season_1)
        cat_1.name = 'cat1'
        cat_1.save()
        cat_2 = Category(parent = season_1)
        cat_2.name = 'cat2'
        cat_2.save()
        cat_3 = Category(parent = season_2)
        cat_3.name = 'cat3'
        cat_3.save()

        course_1 = Course(parent = cat_1)
        course_1.code = 'C1'
        course_1.save()
        course_2 = Course(parent = cat_1)
        course_2.code = 'C2'
        course_2.save()
        course_3 = Course(parent = cat_2)
        course_3.code = 'C3'
        course_3.save()
        course_4 = Course(parent = cat_3)
        course_4.code = 'C4'
        course_4.save()
 
    elif action == 'reset':
        db.delete(Season.all(keys_only=True))
        db.delete(Category.all(keys_only=True))
        db.delete(Course.all(keys_only=True))
        pass
    elif action == 'dump':
        dump_seasons = Season.all()
        dump_categories = Category.all()
        dump_courses = Course.all()
        return render_to_response('school/test_index.html', RequestContext(request, {
            'dump_seasons':dump_seasons,
            'dump_categories':dump_categories,
            'dump_courses':dump_courses,
        }))
        
    
    return render_to_response('school/test_index.html', RequestContext(request))

def courses_index(request):
    return render_to_response('school/courses_index.html', RequestContext(request))

def students_index(request):
    return render_to_response('school/students_index.html', RequestContext(request))

def enrolment_index(request):
    return render_to_response('school/enrolment_index.html', RequestContext(request))




