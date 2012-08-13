# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'^accounts/',include('accounts.urls')),
    (r'^utils/',include('utils.urls')),
    (r'^reports/',include('reports.urls')),
    (r'^vital/',include('vital.urls')),
    (r'^cron_jobs/report_test/', 'reports.views.cron_test'),
    (r'^cron_jobs/report_daily/', 'reports.views.cron_daily'),
    (r'^tasks/register_csv_order/(?P<file_key>[^/]+)/?$', 'vital.views.register_csv_order'),
    (r'^tasks/mail_transaction_report/(?P<account_id>\d+)/$', 'reports.views.task_one_trans_report'),
    (r'^tasks/mail_accounts_report/$', 'reports.views.task_accounts_report'),
    (r'^tasks/do_clearance/(?P<clearance_id>\d+)/$', 'vital.views.task_do_clearance'),
    (r'^tasks/incoming_email/(?P<file_key>[^/]+)/?$', 'emails.views.incoming_email'),
    (r'^tasks/prepare_email_job/(?P<job_id>\d+)/$', 'emails.views.email_job_prepare'),
    (r'^tasks/start_email_job/(?P<job_id>\d+)/$', 'emails.views.email_job_start_task'),
    (r'^tasks/fire_email_subjob/(?P<subjob_key>[^/]+)/$', 'emails.views.fire_email_subjob'),
    (r'^utils/setup/$', 'utils.setup.setup'),
    (r'^$', 'accounts.views.goHome'),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
