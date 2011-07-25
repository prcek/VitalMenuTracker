from django.conf.urls.defaults import *

urlpatterns = patterns('emails.views',
    (r'^$', 'index'),
    (r'^groups/$', 'emailGroups'),
    (r'^groups/(?P<emailGroupId>\d+)/$', 'emailGroupShow'),
    (r'^groups/(?P<emailGroupId>\d+)/edit/$', 'emailGroupEdit'),
    (r'^groups/create/$', 'emailGroupCreate'),

    (r'^templates/$', 'email_template'),
    (r'^templates/(?P<template_id>\d+)/$', 'email_template_show'),
    (r'^templates/(?P<template_id>\d+)/edit/$', 'email_template_edit'),
    (r'^templates/(?P<template_id>\d+)/test_send/$', 'email_template_test_send'),
    (r'^templates/create/$', 'email_template_create'),
    

    (r'^jobs/$', 'email_job'),
    (r'^jobs/(?P<job_id>\d+)/$', 'email_job_show'),
    (r'^jobs/create/$', 'email_job_create'),
    

    (r'^parse_email/(?P<file_key>[^/]+)/?$', 'parse_email'),

)

