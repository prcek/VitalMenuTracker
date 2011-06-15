from django.conf.urls.defaults import *

urlpatterns = patterns('utils.views',
    (r'^$', 'index'),
    (r'^email/$', 'emailFilter'),
    (r'^env/$', 'showEnv'),
    (r'^user/$', 'showUser'),
    (r'^help/$', 'showHelp'),
)

