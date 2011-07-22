from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
import logging, email, time
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

#http://code.google.com/p/googleappengine/issues/detail?id=4872 
#FIXME

    if not blob_key:
        logging.info('again....1')
        time.sleep(1)
        blob_key = files.blobstore.get_blob_key(file_name)

    if not blob_key:
        logging.info('again....2')
        time.sleep(1)
        blob_key = files.blobstore.get_blob_key(file_name)

#endofhack 
        
    logging.info('file key:%s'%blob_key)
    return blob_key



class LogSenderHandler(InboundMailHandler):




    def receive(self, mail_message):

        logging.info('INMAIL_TEST handler')
        logging.info("Received a message from: %s, to: %s" % (mail_message.sender, mail_message.to))
        logging.info("mail date: %s" % mail_message.date)
        logging.info("subject: %s" % mail_message.subject)

        data = mail_message.to_mime_message()
        logging.info(data)


def main():
    application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

