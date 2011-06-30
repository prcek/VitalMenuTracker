from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib
import logging


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            for upload in self.get_uploads():
                logging.info('upload done - key:"%s"'%upload.key())
            self.redirect('/utils/files/')
        except:
            self.redirect('/utils/files/upload_error_gae/')

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, key):
        key = str(urllib.unquote(key))
        logging.info('download key:"%s"'%key)
        if not blobstore.get(key):
            self.error(404)
        else:
            blob_info = blobstore.BlobInfo.get(key)
            self.send_blob(key,save_as=blob_info.filename) 

application = webapp.WSGIApplication([('/upload', UploadHandler),
                                      ('/download/([^/]+)?/?', DownloadHandler),
                                     ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
