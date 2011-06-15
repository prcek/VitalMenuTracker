from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
    (r'^$', 'index'),
    (r'^show/$', 'show_all'),
    (r'^show/(?P<account_id>\d+)/$', 'show_account'),
    (r'^edit/(?P<account_id>\d+)/$', 'edit_account'),
    (r'^create/$', 'create_account'),
    (r'^update/(?P<account_id>\d+)/$', 'update_balance'),
)
