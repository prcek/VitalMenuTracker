from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
    (r'^$', 'account_list'),
    (r'^create/$', 'account_create'),
    (r'^(?P<account_id>\d+)/$', 'account_show'),
    (r'^(?P<account_id>\d+)/edit/$', 'account_edit'),
    (r'^(?P<account_id>\d+)/transactions/$', 'transaction_list'),
#    (r'^(?P<account_id>\d+)/transactions/(?P<transaction_id>\d+)/$', 'transaction_show'),
    (r'^(?P<account_id>\d+)/transactions/create/$', 'transaction_create'),
)
