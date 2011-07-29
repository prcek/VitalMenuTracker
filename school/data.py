from utils.data import CSVBlobReader
from school.models import Season,Category,Course,Group,Student
import logging

def get_or_create_season(season_name):
    season = Season.all().filter('name',season_name).get()
    if season is None:
        season = Season()
        season.name = season_name
        season.save()
    return season

def get_or_create_category(season,category_name):
    category = Category.all().ancestor(season).filter('name',category_name).get()
    if category is None:
        category = Category(parent=season)
        category.name = category_name
        category.save()
    return category

def get_or_create_course(category,course_code):
    course = Course.all().ancestor(category).filter('code',course_code).get()
    if course is None:
        course = Course(parent=category)
        course.code = course_code
        course.save()
    return course

def update_course(course, print_line_1=None, print_line_2=None, group_mode=None, name=None):
    s=False 
    if print_line_1:
        course.print_line_1 = print_line_1
        s = True
    if print_line_2:
        course.print_line_2 = print_line_2
        s = True
    if group_mode:
        course.group_mode = group_mode
        s = True
    if name:
        course.name = name
        s = True
    if s:
        course.save()

def import_test(file_key):
    csv = CSVBlobReader(file_key,encoding='utf-8', delimiter=',', quotechar='"')
    for row in csv:
        try:
            if row[0].startswith('#export kurz'):
                season = get_or_create_season(row[3])    
                category = get_or_create_category(season,row[2])
                course = get_or_create_course(category,row[1])
                update_course(course,print_line_1=row[4],print_line_2=row[5],name=row[6])
                logging.info(row)
        except:
            logging.info("can't process row=%s"%row)
