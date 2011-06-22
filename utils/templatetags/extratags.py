from django import template
from django.utils import html
from utils import menu;
from google.appengine.api import users


register = template.Library()

def isAuthFor(userS,actionS):
    return False

class RenderMenuNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        t = template.loader.get_template('menu.html')
        current_menu = menu.app_menu; 
        
        


        if 'request' in context:
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

        for m in current_menu:
            if 'access' in m:
                pass
            if 'submenu' in m:
                for s in m['submenu']:
                    if 'access' in s:
                        pass
                

        return t.render(template.Context({'menu':current_menu}))

@register.tag
def render_menu(parser, token):
    return RenderMenuNode() 


class RenderUserNode(template.Node):
    def __init__(self):
        pass
    def render(self, context):
        t = template.loader.get_template('user.html')

        if 'request' in context:
            base_uri = context['request'].path
        else:
            base_uri = ""

        auth = False
        admin_user =  False
        power_user = False
        username = ""
        user = users.get_current_user()
        logout_url = users.create_logout_url(base_uri);
        login_url = users.create_login_url(base_uri);
        if user:
            username = user.nickname()
            auth = True
            admin_user = users.is_current_user_admin()
        return t.render(template.Context({'username':username, 'auth':auth, 'login_url':login_url, 'logout_url':logout_url, 'admin':admin_user, 'power':power_user}))

@register.tag
def render_user(parser, token):
    return RenderUserNode() 
