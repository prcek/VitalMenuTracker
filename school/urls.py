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
    (r'^students/$', 'students_index'),
    (r'^enrolment/$', 'enrolment_index'),
)

