from django import template
from django.utils import html
from utils import menu;
from google.appengine.api import users
from utils.models import User

register = template.Library()

def isAuthFor(ua,a):
    if ua.admin:
        return True

    if a == 'a':
        return False

    if ua.power and a=='p':
        return True

    if ua.auth and a=='u':
        return True
    
    return False

class RenderMenuNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        t = template.loader.get_template('menu.html')
        current_menu = menu.app_menu; 
        
        if not 'request' in context:
            return ''

        path = context['request'].path
        for m in current_menu:
            if 'url' in m:
                if path.startswith(m['url']):
                    m['active']=1;
                    if 'submenu' in m:
                        for s in m['submenu']:
                            if 'url' in s:
                                if path == s['url']:
                                    s['active']=1
                                else:
                                    s['active']=0
                            else:
                                s['active']=0

                else:
                    m['active']=0
            else:
                m['active']=0

        ua = context['request'].auth_info
        for m in current_menu:
            if ('access' in m) and not isAuthFor(ua, m['access']):
                m['hide']=1
            else:
                m['hide']=0
        
            if 'submenu' in m:
                for s in m['submenu']:
                    if ('access' in s) and not isAuthFor(ua, s['access']):
                        s['hide']=1
                    else:
                        s['hide']=0

        return t.render(template.Context({'menu':current_menu}))

@register.tag
def render_menu(parser, token):
    return RenderMenuNode() 


class RenderUserNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        t = template.loader.get_template('user.html')
        return t.render(context)

@register.tag
def render_user(parser, token):
    return RenderUserNode() 
