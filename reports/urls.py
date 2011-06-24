from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    (r'^$', 'index'),
    (r'^cron_test/$', 'cron_test'),
    (r'^cron_daily/$', 'cron_daily'),
)
