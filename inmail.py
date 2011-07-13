import logging, email
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: %s" % mail_message.sender)
        logging.info("mail date: %s" % mail_message.date)

        if hasattr(mail_message, "attachment"):
            for a in mail_message.attachments:
                logging.info('attachment name %s'% a[0])
        else:
            logging.info('no attachment')

application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

