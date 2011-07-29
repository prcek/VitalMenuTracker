# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.decorators import user_required, power_required, admin_required, cron_required


from utils.mail import send_mail_to_admins, send_mail_to_user
from utils.config import getConfig

from google.appengine.api import taskqueue
from google.appengine.ext import db
from school.models import Season,Category,Course,Group,Student
import school.data
import logging


def get_actual_season():
    s = Season.all().filter('actual =',True).get()
    if s is None:
        s = Season.all().get()
    return s

def get_actual_category_for_season(season):
    return Category.all().ancestor(season).get()

def get_actual_course_for_category(category):
    return Course.all().ancestor(category).get()


def get_actual_season_and_category():
    season = get_actual_season()
    cat = get_actual_category_for_season(season)
    return (season,cat)
    

def get_season_navi_list(actual=None):
    result = []    
    slist = Season.all().filter('hidden !=',True)
    for s in slist:
        if actual and s.key() == actual.key():
            selected = True
        else:
            selected = False
        result.append({'label':s.name,'value':s.key().id(), 'selected':selected})

    return result

def get_category_navi_list(season, actual=None):
    result = []    
    clist = Category.all().ancestor(season).filter('hidden !=',True)
    for c in clist:
        if actual and c.key() == actual.key():
            selected = True
        else:
            selected = False
        result.append({'label':c.name,'value':c.key().id(), 'selected':selected})

    return result
    

def get_course_navi_list(season_key, actual=None):
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
            sub_list = [{'label':c.code, 'value':'%s/%s'%(category.key().id(),c.key().id()), 'selected':(actual and c.key()==actual.key())} for c in courses if c.parent_key()==category.key()] 
            result.append({'label':category.name,'value':category.key(), 'list':sub_list})
    return result 

def get_students(parent):

    result = []
    if isinstance(parent,Course):
        course = parent
        students_query = Student.all().ancestor(course)
        groups_query = Group.all().ancestor(course)
        gr_set = set([])
        students = []
   
        for student in students_query:
            group_key = student.parent_key()  
            gr_set.add(group_key)
            students.append(student)

        for group in groups_query:
            if group.key() in gr_set:
                sub_list = [ s for s in students if s.parent_key()==group.key()] 
                result.append({'group':group,'students':sub_list})
            else:
                result.append({'group':group,'students':[]})

    elif isinstance(parent,Group):
        group = parent 
        students_query = Student.all().ancestor(group)
        students = []
        for student in students_query:
            students.append(student)

        result.append({'group':group,'students':students})

    
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


        group_1 = Group(parent = course_1)
        group_1.name = 'g1'
        group_1.save()

        group_2 = Group(parent = course_1)
        group_2.name = 'g2'
        group_2.save()

        group_3 = Group(parent = course_1)
        group_3.name = 'g3'
        group_3.save()



        student_1_1 = Student(parent = group_1)
        student_1_1.name = 'st1'
        student_1_1.save()
        
        student_1_2 = Student(parent = group_1)
        student_1_2.name = 'st2'
        student_1_2.save()
 
        student_2_1 = Student(parent = group_2)
        student_2_1.name = 'st3'
        student_2_1.save()
 
 
    elif action == 'reset':
        db.delete(Season.all(keys_only=True))
        db.delete(Category.all(keys_only=True))
        db.delete(Course.all(keys_only=True))
        db.delete(Group.all(keys_only=True))
        db.delete(Student.all(keys_only=True))
    elif action == 'dump':
        dump_seasons = Season.all()
        dump_categories = Category.all()
        dump_courses = Course.all()
        dump_groups = Group.all()
        dump_students = Student.all()
        return render_to_response('school/test_index.html', RequestContext(request, {
            'dump_seasons':dump_seasons,
            'dump_categories':dump_categories,
            'dump_courses':dump_courses,
            'dump_groups':dump_groups,
            'dump_students':dump_students,
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

    if request.method == 'POST':
        ss = request.POST['switch_season']
        return HttpResponseRedirect('../%s/'%ss)


    if season_id is None:
        season_id = get_actual_season().key().id()
        return redirect('%d/'%season_id)

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    snl = get_season_navi_list(season)

    categories = Category.all().ancestor(season)
    
    return render_to_response('school/categories_index.html', RequestContext(request, {'category_list': categories, 'season':season, 'season_navi_list':snl}))

def get_season_and_category(season_id, category_id):
    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404

    category = Category.get_by_season_and_id(season,int(category_id))
    if category is None:
        raise Http404
   
    return (season,category) 

def category_show(request,season_id, category_id):

    (season,category) = get_season_and_category(season_id, category_id)

    return render_to_response('school/category_show.html', RequestContext(request, {'season':season, 'category':category}))

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ( 'name','hidden' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



def category_edit(request,season_id, category_id):

    (season,category) = get_season_and_category(season_id, category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            logging.info('edit category before %s'% category)
            form.save(commit=False)
            logging.info('edit category after %s'% category)
            category.save()
            return redirect('../..')
    else:
        form = CategoryForm(instance=category)

    return render_to_response('school/category_edit.html', RequestContext(request, {'form':form}))

def category_create(request, season_id):
    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404


    category = Category(parent=season)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            logging.info('edit category before %s'% category)
            form.save(commit=False)
            logging.info('edit category after %s'% category)
            category.save()
            return redirect('..')
    else:
        form = CategoryForm(instance=category)
    return render_to_response('school/category_create.html', RequestContext(request, {'form':form}))



def courses_index(request, season_id=None, category_id=None):

    if request.method == 'POST':
        if 'switch_season' in request.POST:
            ss = request.POST['switch_season']
            return HttpResponseRedirect('../../%s/'%ss)
        if 'switch_category' in request.POST:
            sc = request.POST['switch_category']
            return HttpResponseRedirect('../%s/'%sc)



    if season_id is None:  
        season = get_actual_season()
        return redirect('%d/'%season.key().id())

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404
  
    if category_id is None:
        category = get_actual_category_for_season(season) 
        return redirect('%d/'%category.key().id())

    category = Category.get_by_season_and_id(season,int(category_id))
    if category is None:
        raise Http404
 
    snl = get_season_navi_list(season)
    cnl = get_category_navi_list(season,category)

    courses = Course.all().ancestor(category)
    
    return render_to_response('school/courses_index.html', RequestContext(request, {'courses_list': courses, 'category':category, 'season':season, 'category_navi_list':cnl, 'season_navi_list':snl}))


def get_season_and_category_and_course(season_id, category_id, course_id):
    (season,category) = get_season_and_category(season_id, category_id)

    course = Course.get_by_category_and_id(category,int(course_id))
    if course is None:
        raise Http404
   
    return (season,category, course) 


def course_show(request,season_id, category_id, course_id):

    (season,category,course) = get_season_and_category_and_course(season_id, category_id, course_id)

    return render_to_response('school/course_show.html', RequestContext(request, {'season':season, 'category':category, 'course':course}))

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ( 'code','name','group_mode','print_line_1', 'print_line_2', 'hidden' )

    def clean_code(self):
        data = self.cleaned_data['code']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



def course_edit(request,season_id, category_id, course_id):

    (season,category,course) = get_season_and_category_and_course(season_id, category_id, course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.save()
            return redirect('../..')
    else:
        form = CourseForm(instance=course)

    return render_to_response('school/course_edit.html', RequestContext(request, {'form':form}))

def course_create(request, season_id, category_id):
    (season,category) = get_season_and_category(season_id, category_id)

    course = Course(parent=category)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            logging.info('edit course before %s'% course)
            form.save(commit=False)
            logging.info('edit course after %s'% course)
            course.save()
            return redirect('..')
    else:
        form = CourseForm(instance=course)
    return render_to_response('school/course_create.html', RequestContext(request, {'form':form}))





def students_index(request, season_id=None, category_id=None, course_id=None):

    if request.method == 'POST':
        if 'switch_season' in request.POST:
            ss = request.POST['switch_season']
            return HttpResponseRedirect('../../../%s/'%ss)
        if 'switch_course' in request.POST:
            sc = request.POST['switch_course']
            return HttpResponseRedirect('../../%s/'%sc)



    if season_id is None:  
        season = get_actual_season()
        return redirect('%d/'%season.key().id())

    season = Season.get_by_id(int(season_id))
    if season is None:
        raise Http404
  
    if category_id is None:
        category = get_actual_category_for_season(season) 
        return redirect('%d/'%category.key().id())

    category = Category.get_by_season_and_id(season,int(category_id))
    if category is None:
        raise Http404
 
    if course_id is None:
        course = get_actual_course_for_category(category) 
        return redirect('%d/'%course.key().id())

    course = Course.get_by_category_and_id(category,int(course_id))
    if course is None:
        raise Http404
 
    snl = get_season_navi_list(season)
    cnl = get_course_navi_list(season,course)

    students = get_students(course)
    logging.info(students)

    return render_to_response('school/students_index.html', RequestContext(request, {'season':season, 'category':category, 'course':course, 'students':students, 'season_navi_list':snl, 'course_navi_list':cnl}))


def get_season_and_category_and_course_and_group(season_id, category_id, course_id, group_id):
    (season,category,course) = get_season_and_category_and_course(season_id, category_id, course_id)

    group = Group.get_by_course_and_id(course,int(group_id))
    if group is None:
        raise Http404
   
    return (season,category, course, group) 


def group_index(request, season_id, category_id, course_id, group_id):

    (season,category,course,group) = get_season_and_category_and_course_and_group(season_id, category_id, course_id, group_id)
    students = get_students(group)

    return render_to_response('school/group_index.html', RequestContext(request, {'season':season, 'category':category, 'course':course, 'group': group, 'students':students}))

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group 
        fields = ( 'name','invisible' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



def group_create(request, season_id, category_id, course_id):
    (season,category,course) = get_season_and_category_and_course(season_id, category_id, course_id)

    group = Group(parent=course)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            logging.info('edit group before %s'% group)
            form.save(commit=False)
            logging.info('edit group after %s'% group)
            group.save()
            return redirect('..')
    else:
        form = GroupForm(instance=group)
    return render_to_response('school/group_create.html', RequestContext(request, {'form':form}))

def group_edit(request, season_id, category_id, course_id, group_id):

    (season,category,course,group) = get_season_and_category_and_course_and_group(season_id, category_id, course_id, group_id)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            logging.info('edit group before %s'% group)
            form.save(commit=False)
            logging.info('edit group after %s'% group)
            group.save()
            return redirect('../..')
    else:
        form = GroupForm(instance=group)

    return render_to_response('school/group_edit.html', RequestContext(request, {'form':form}))

def get_season_and_category_and_course_and_group_and_student(season_id, category_id, course_id, group_id, student_id):
    (season,category,course,group) = get_season_and_category_and_course_and_group(season_id, category_id, course_id, group_id)

    student = Student.get_by_group_and_id(group,int(student_id))
    if student is None:
        raise Http404
   
    return (season,category, course, group, student) 



def student_index(request, season_id, category_id, course_id, group_id, student_id):

    (season,category,course,group,student) = get_season_and_category_and_course_and_group_and_student(season_id, category_id, course_id, group_id, student_id)

    return render_to_response('school/group_index.html', RequestContext(request, {'season':season, 'category':category, 'course':course, 'group': group, 'student':student}))

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ( 'name' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



def student_create(request, season_id, category_id, course_id, group_id):
    (season,category,course, group) = get_season_and_category_and_course_and_group(season_id, category_id, course_id, group_id)

    student = Student(parent=group)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('edit student before %s'% student)
            form.save(commit=False)
            logging.info('edit student after %s'% student)
            student.save()
            return redirect('..')
    else:
        form = StudentForm(instance=student)
    return render_to_response('school/student_create.html', RequestContext(request, {'form':form}))

def student_edit(request, season_id, category_id, course_id, group_id, student_id):

    (season,category,course,group,student) = get_season_and_category_and_course_and_group_and_student(season_id, category_id, course_id, group_id, student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            logging.info('edit student before %s'% student)
            form.save(commit=False)
            logging.info('edit student after %s'% student)
            student.save()
            return redirect('../..')
    else:
        form = StudentForm(instance=student)

    return render_to_response('school/student_edit.html', RequestContext(request, {'form':form}))


def import_csv_backup(request,file_key):
    result = school.data.import_test(file_key)
    return HttpResponse(result)

def enrolment_index(request):
    return render_to_response('school/enrolment_index.html', RequestContext(request))




