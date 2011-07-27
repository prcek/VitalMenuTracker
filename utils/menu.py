
app_menu = [ 
    {'name':'accounts', 'url':'/accounts/', 'access':'u',
     'submenu': [ 
                    { 'name':'list', 'url':'/accounts/' },
                ]
    },
    {'name':'emails', 'url':'/emails/' , 'access':'u',
     'submenu': [
                    { 'name':'groups', 'url':'/emails/groups/' },
                    { 'name':'templates', 'url':'/emails/templates/' },
                    { 'name':'jobs', 'url':'/emails/jobs/' },
                ]
    },

    {'name':'utils', 'url':'/utils/' ,
     'submenu': [
                    { 'name':'filter', 'url':'/utils/email/' },
                    { 'name':'env', 'url':'/utils/env/', 'access':'u' },
                    { 'name':'user', 'url':'/utils/user/', 'access':'u' },
                    { 'name':'users', 'url':'/utils/users/', 'access':'a' },
                    { 'name':'config', 'url':'/utils/config/', 'access':'a' },
                    { 'name':'help', 'url':'/utils/help/', 'access':'u' },
                    { 'name':'pdf_test', 'url':'/utils/pdf_test/', 'access':'a' },
                    { 'name':'csv_test', 'url':'/utils/csv_test/', 'access':'a' },
                    { 'name':'captcha', 'url':'/utils/captcha/', 'access':'a' },
                    { 'name':'files', 'url':'/utils/files/', 'access':'a' },
                    { 'name':'debug', 'url':'/utils/debug/', 'access':'p'  },
                ]
    },

    {'name':'reports', 'url':'/reports/' ,
     'submenu': [
                    { 'name':'index', 'url':'/reports/' },
                    { 'name':'execute_cron_test', 'url':'/reports/cron_test/', 'access':'a' },
                    { 'name':'execure_cron_daily', 'url':'/reports/cron_daily/', 'access':'a' },
                ]
    },
    
    {'name':'vital', 'url':'/vital/',
     'submenu': [
                    { 'name':'index', 'url':'/vital/', 'access':'u' },
                    { 'name':'clearance', 'url':'/vital/clearance/', 'access':'p' },
                    { 'name':'extra', 'url':'/vital/extra/', 'access':'p' },
                    { 'name':'orders', 'url':'/vital/orders/', 'access':'p' }
                ]
    },
    {'name':'school', 'url':'/school/', 'access':'a',
     'submenu': [
                    { 'name':'index', 'url':'/school/', 'access':'a' },
                    { 'name':'test', 'url':'/school/test/', 'access':'a' },
                    { 'name':'test_navi', 'url':'/school/test_navi/', 'access':'a' },
                    { 'name':'seasons', 'url':'/school/seasons/', 'access':'a' },
                    { 'name':'categories', 'url':'/school/categories/', 'access':'a' },
                    { 'name':'courses', 'url':'/school/courses/', 'access':'a' },
                    { 'name':'students', 'url':'/school/students/', 'access':'a' },
                    { 'name':'enrolment', 'url':'/school/enrolment/', 'access':'a' },
                ]
    },



 ]

