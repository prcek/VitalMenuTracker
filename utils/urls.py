from django.conf.urls.defaults import *

urlpatterns = patterns('utils.views',
    (r'^$', 'index'),
    (r'^email/$', 'emailFilter'),
    (r'^env/$', 'showEnv'),
    (r'^user/$', 'showUser'),
    (r'^users/$', 'user_list'),
    (r'^users/create/$', 'user_create'),
    (r'^users/(?P<user_id>\d+)/$', 'user_show'),
    (r'^users/(?P<user_id>\d+)/edit/$', 'user_edit'),
    (r'^config/$', 'config_list'),
    (r'^config/create/$', 'config_create'),
    (r'^config/(?P<config_id>\d+)/$', 'config_show'),
    (r'^config/(?P<config_id>\d+)/edit/$', 'config_edit'),
    (r'^help/$', 'showHelp'),
    (r'^debug/$', 'debugTest'),
)

