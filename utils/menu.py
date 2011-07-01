
app_menu = [ 
    {'name':'accounts', 'url':'/accounts/', 'access':'u',
     'submenu': [ 
                    { 'name':'list', 'url':'/accounts/' },
                ]
    },
    {'name':'emails', 'url':'/emails/' , 'access':'u',
     'submenu': [
                    { 'name':'groups', 'url':'/emails/groups/' },
                    { 'name':'create group', 'url':'/emails/groups/create/' },
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

 ]

