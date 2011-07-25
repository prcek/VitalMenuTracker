from appengine_django.models import BaseModel
from google.appengine.ext import db
import re
import os

# Create your models here.
class EMailList(BaseModel):
    name = db.StringProperty()
    desc = db.StringProperty()
    emails = db.StringListProperty() 

    def emailsAsString(self,sep=' '):
        f = True
        o = ''
        for e in self.emails:
            if f:
                f = False
            else:
                o += sep
            o += e
        return o
    
    def emailsFromString(self,text):
        text = re.sub(r'[,;]'," ",text)
        s = set([])
        for e in text.split():
            if  re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$",e) != None:
                s.add(e)
        self.emails=[]
        for e in sorted(s):
            self.emails.append(e)
                

class EMailTemplate(BaseModel):
    name = db.StringProperty()
    data = db.BlobProperty()            
    open_for_import = db.BooleanProperty()

    def import_email(self):
        return "import-email-%d@%s.%s"%(self.key().id(),os.environ['APPLICATION_ID'],'appspotmail.com') 

    def blob_info(self):
        if self.data is None:
            return "no data"
        return "size=%d"%len(self.data)
