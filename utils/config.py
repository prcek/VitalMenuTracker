from utils.models import Config

def getConfig(name, dv=None):
    c = Config.objects.all().filter('name =',name).filter('active = ',True).get()
    if c:
        return c.value
    return dv 
