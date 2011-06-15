from django.conf.urls.defaults import *

urlpatterns = patterns('emails.views',
    (r'^$', 'index'),
    (r'^groups/$', 'emailGroups'),
    (r'^groups/(?P<emailGroupId>\d+)/$', 'emailGroupShow'),
    (r'^groups/edit/(?P<emailGroupId>\d+)/$', 'emailGroupEdit'),
    (r'^groups/create/$', 'emailGroupCreate'),
)

