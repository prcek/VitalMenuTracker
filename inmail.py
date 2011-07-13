from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
import logging, email
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import taskqueue

def store_raw_data_as_blob(data,name,content_type):
    logging.info('store (bin) raw_data as %s (%s)'%(name,content_type))
    file_name = files.blobstore.create(mime_type=content_type, _blobinfo_uploaded_filename = name)
    with files.open(file_name, 'a') as out:
        out.write(data)
    files.finalize(file_name)
    blob_key = files.blobstore.get_blob_key(file_name)
    logging.info('file key:%s'%blob_key)
    return blob_key

def plan_import_task(fk=None):
    logging.info('plan_import_task')
    if fk is None:
        return
    logging.info('key = %s'%fk)
    taskqueue.add(url='/vital/register_csv_order/%s/'%fk, method='GET')
    



class LogSenderHandler(InboundMailHandler):




    def receive(self, mail_message):


        logging.info("Received a message from: %s, to: %s" % (mail_message.sender, mail_message.to))
        logging.info("mail date: %s" % mail_message.date)
        logging.info("subject: %s" % mail_message.subject)



        if mail_message.subject.startswith('test'):
            plaintext_bodies = mail_message.bodies('text/plain')
            for c,b in plaintext_bodies:
                fk = store_raw_data_as_blob(b.decode(),'test','text/plain')
                plan_import_task(fk)
            return
        
        plaintext_bodies = mail_message.bodies('text/plain')
        for c,b in plaintext_bodies:
            logging.info('%s' % b.decode()) 

        if hasattr(mail_message, "attachments"):
            for name,content in mail_message.attachments:
                logging.info('attachment name %s'% name)
                logging.info('attachment content %s'% content)
                logging.info('attachment content charset %s'% content.charset)
                if not content.charset:
                    content.charset='windows-1250'
                    logging.info('attachment content NEW charset %s'% content.charset)
                logging.info('attachment decode %s'%content.decode())
                if name.endswith('.csv'):
                    fk = store_raw_data_as_blob(content.decode().encode('utf-8'),name,'text/csv')
                    plan_import_task(fk)
                else:
                    logging.info('no csv')
        else:
            logging.info('no attachment')


def main():
    application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

