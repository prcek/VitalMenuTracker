from django.conf.urls.defaults import *

urlpatterns = patterns('school.views',
    (r'^$', 'index'),
    (r'^test/$', 'test_index'),
    (r'^test_navi/$', 'test_navi'),
    (r'^seasons/$', 'seasons_index'),
    (r'^seasons/create/$', 'season_create'),
    (r'^seasons/(?P<season_id>\d+)/$', 'season_show'),
    (r'^seasons/(?P<season_id>\d+)/edit/$', 'season_edit'),
    (r'^categories/$', 'categories_index'),
    (r'^categories/(?P<season_id>\d+)/$', 'categories_index'),
    (r'^categories/(?P<season_id>\d+)/create/$', 'category_create'),
    (r'^categories/(?P<season_id>\d+)/(?P<category_id>\d+)/$', 'category_show'),
    (r'^categories/(?P<season_id>\d+)/(?P<category_id>\d+)/edit/$', 'category_edit'),
    (r'^courses/$', 'courses_index'),
    (r'^courses/(?P<season_id>\d+)/$', 'courses_index'),
    (r'^courses/(?P<season_id>\d+)/(?P<category_id>\d+)/$', 'courses_index'),
    (r'^courses/(?P<season_id>\d+)/(?P<category_id>\d+)/create/$', 'course_create'),
    (r'^courses/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/$', 'course_show'),
    (r'^courses/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/edit/$', 'course_edit'),
    (r'^students/$', 'students_index'),
    (r'^students/(?P<season_id>\d+)/$', 'students_index'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/$', 'students_index'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/$', 'students_index'),


    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/(?P<group_id>\d+)/$', 'group_index'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/(?P<group_id>\d+)/edit/$', 'group_edit'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/create/$', 'group_create'),


    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/(?P<group_id>\d+)/create/$', 'student_create'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/(?P<group_id>\d+)/(?P<student_id>\d+)/$', 'student_index'),
    (r'^students/(?P<season_id>\d+)/(?P<category_id>\d+)/(?P<course_id>\d+)/(?P<group_id>\d+)/(?P<student_id>\d+)/edit/$', 'student_edit'),

    (r'^enrolment/$', 'enrolment_index'),
)

