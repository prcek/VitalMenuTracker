# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from google.appengine.api import taskqueue
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
