
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
                    { 'name':'help', 'url':'/utils/help/', 'access':'u' },
                ]
    },
 ]

