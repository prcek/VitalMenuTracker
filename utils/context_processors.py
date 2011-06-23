import logging
def auth(request):
    logging.info('context processor - auth')
    return {'dest':'sss'}
