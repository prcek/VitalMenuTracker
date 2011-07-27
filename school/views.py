# Create your views here.
from django.http import HttpResponse, Http404
from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from google.appengine.api import taskqueue
from google.appengine.ext import db
from school.models import Season,Category,Course,Group,Student

import logging


def get_actual_season():
    s = Season.all().filter('actual =',True).get()
    if s is None:
        s = Season.all().get()
    return s
    

def get_course_navi_list(season_key):
    logging.info('get_course_navi_list for key:%s',season_key) 
    courses_query = Course.all().ancestor(season_key)
    categories_query = Category.all().ancestor(season_key)
    cat_set = set([])
    courses = []
    result = []
    for course in courses_query:
        category_key = course.parent_key()
        cat_set.add(category_key)
        courses.append(course)
    for category in categories_query:
        if category.key() in cat_set:
            sub_list = [{'label':c.code, 'value':c.key()} for c in courses if c.parent_key()==category.key()] 
            result.append({'label':category.name,'value':category.key(), 'list':sub_list})
    return result 


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


def test_navi(request):
    season = get_actual_season()
    if season is None:
        raise Http404
    navi_list = get_course_navi_list(season.key())
    return render_to_response('school/test_navi.html', RequestContext(request, {'list':navi_list}))

def seasons_index(request):
#    seasons = Season.all().filter('hidden=',False)
    seasons = Season.all()
    return render_to_response('school/seasons_index.html', RequestContext(request, {'season_list':seasons}))

def season_show(request,season_id):
    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404
    return render_to_response('school/season_show.html', RequestContext(request, {'season':season}))

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ( 'name','hidden','actual' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



def season_edit(request,season_id):
    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404
    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            logging.info('edit season before %s'% season)
            form.save(commit=False)
            logging.info('edit season after %s'% season)
            season.save()
            return redirect('../..')
    else:
        form = SeasonForm(instance=season)

    return render_to_response('school/season_edit.html', RequestContext(request, {'form':form}))

def season_create(request):
    season = Season()
    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            logging.info('edit season before %s'% season)
            form.save(commit=False)
            logging.info('edit season after %s'% season)
            season.save()
            return redirect('..')
    else:
        form = SeasonForm(instance=season)
    return render_to_response('school/season_create.html', RequestContext(request, {'form':form}))

def categories_index(request, season_id=None):
    if season_id is None:
        season_id = get_actual_season().key().id()
        return redirect('%d/'%season_id)

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404


    categories = Category.all().ancestor(season)

    
    return render_to_response('school/categories_index.html', RequestContext(request, {'category_list': categories}))

def courses_index(request):
    return render_to_response('school/courses_index.html', RequestContext(request))

def students_index(request):
    return render_to_response('school/students_index.html', RequestContext(request))

def enrolment_index(request):
    return render_to_response('school/enrolment_index.html', RequestContext(request))




