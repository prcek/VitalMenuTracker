
app_menu = [ 
    {'name':'accounts', 'url':'/accounts/',
     'submenu': [ 
                    { 'name':'list', 'url':'/accounts/' },
                ]
    },
    {'name':'emails', 'url':'/emails/' ,
     'submenu': [
                    { 'name':'groups', 'url':'/emails/groups/' },
                    { 'name':'create group', 'url':'/emails/groups/create/' },
                ]
    },

    {'name':'utils', 'url':'/utils/' ,
     'submenu': [
                    { 'name':'filter', 'url':'/utils/email/' },
                    { 'name':'env', 'url':'/utils/env/' },
                    { 'name':'user', 'url':'/utils/user/' },
                    { 'name':'help', 'url':'/utils/help/' },
                ]
    },
 ]

