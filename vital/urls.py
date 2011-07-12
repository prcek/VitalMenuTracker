from django.conf.urls.defaults import *

urlpatterns = patterns('vital.views',
    (r'^$', 'index'),
    (r'^register_csv_order/(?P<file_key>[^/]+)/?$', 'register_csv_order'),
)

