from django.conf.urls.defaults import *

urlpatterns = patterns('school.views',
    (r'^$', 'index'),
    (r'^test/$', 'test_index'),
    (r'^courses/$', 'courses_index'),
    (r'^students/$', 'students_index'),
    (r'^enrolment/$', 'enrolment_index'),
)

