from django.conf.urls.defaults import *

urlpatterns = patterns('vital.views',
    (r'^$', 'index'),
    (r'^orders/$','orders'),
    (r'^register_csv_order/(?P<file_key>[^/]+)/?$', 'register_csv_order'),
    (r'^show_csv_order/(?P<file_key>[^/]+)/?$', 'show_csv_order'),
)

