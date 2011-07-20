from django.conf.urls.defaults import *

urlpatterns = patterns('vital.views',
    (r'^$', 'index'),
    (r'^(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)/?$', 'index_day'),
    (r'^orders/$','orders'),
    (r'^extra/$','extra'),
    (r'^clearance/$','clearance_index'),
    (r'^clearance/(?P<clearance_id>\d+)/$', 'clearance_show'),
    (r'^clearance/(?P<clearance_id>\d+)/edit/$', 'clearance_edit'),
    (r'^clearance/(?P<clearance_id>\d+)/commit/$', 'clearance_commit'),
    (r'^clearance/create/$', 'clearance_create'),
    (r'^register_csv_order/(?P<file_key>[^/]+)/?$', 'register_csv_order'),
    (r'^show_csv_order/(?P<file_key>[^/]+)/?$', 'show_csv_order'),
)

