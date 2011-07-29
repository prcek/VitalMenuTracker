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


def int_or_none(i):
    res = None
    try:
        res = int(i)
    except:
        res = None
    return res 

def sex_or_none(s):
    #s, d, p
    if s in ['s','d','p']:
        return s
    return None

def bool_or_none(v):
    if v:
        if v.lower() in ['ano','1','true']:
            return True        
        if v.lower() in ['ne','0','false']:
            return False
    return None


def import_test(file_key):
    csv = CSVBlobReader(file_key,encoding='utf-8', delimiter=',', quotechar='"')
    course = None
    course_students = []
    to_import = []
    for row in csv:
        try:
            if row[0].startswith('#export kurz'):
                if course and len(course_students):
                    to_import.append((course,course_students))
                    course = None
                    course_students=[]
                try:
                    season = get_or_create_season(row[3])    
                    category = get_or_create_category(season,row[2])
                    course = get_or_create_course(category,row[1])
                    gmode = row[7]   # 0 - flat/group, 1 - pair
                    if gmode == 0:
                        gmode = 'Flat'
                    elif gmode == 1:
                        gmode = 'Pair'
                    else:
                        gmode = None
                    update_course(course,print_line_1=row[4],print_line_2=row[5],name=row[6], group_mode=gmode)
#                    logging.info(course)
                except:
                    logging.info('course row import problem %s'%row)
            elif course:
                try:
                    s = { 
                        'seq_no_1' : int_or_none(row[0]), 
                        'seq_no_2' : int_or_none(row[1]),
                        'sex' : sex_or_none(row[2]),
                        'surname' : row[3],
                        'name' : row[4],
                        'payment' : int_or_none(row[5]),
                        'to_pay' : int_or_none(row[6]),
                        'payment_info' : row[7],
                        'school' : row[8],
                        'school_class' : row[9],
                        'a_street' : row[10],
                        'a_no' : row[11],
                        'a_city' : row[12],
                        'a_post_code' : row[13],
                        'phone' : row[14],
                        'email' : row[15],
                        'spam' : bool_or_none(row[16]),
                        'student' : bool_or_none(row[17]),
                        'student_check' :  bool_or_none(row[18]),
                        'comment' : row[19],
                        }
#                    logging.info(s)
                    course_students.append(s)
                except:
                    logging.info('student row import problem %s'%row)
                
        except:
            logging.info("can't process row=%s"%row)

    if course and len(course_students):
        to_import.append((course,course_students))


    for course,students in to_import:
        logging.info('code=%s, students=%d'%(course.code,len(students)))
    

