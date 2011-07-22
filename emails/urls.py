from django.conf.urls.defaults import *

urlpatterns = patterns('emails.views',
    (r'^$', 'index'),
    (r'^groups/$', 'emailGroups'),
    (r'^groups/(?P<emailGroupId>\d+)/$', 'emailGroupShow'),
    (r'^groups/edit/(?P<emailGroupId>\d+)/$', 'emailGroupEdit'),
    (r'^groups/create/$', 'emailGroupCreate'),
    (r'^parse_email/(?P<file_key>[^/]+)/?$', 'parse_email'),

)

