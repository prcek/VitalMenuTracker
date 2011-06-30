from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
from django.http import HttpResponse, Http404
import logging

def handle_uploaded_file(f):
    logging.info('handle_uploaded_file filename="%s", size=%d, content_type="%s" '%(f.name,f.size,f.content_type))
    file_name = files.blobstore.create(mime_type=f.content_type, _blobinfo_uploaded_filename = f.name)

    with files.open(file_name, 'a') as out:
        for chunk in f.chunks():
            out.write(chunk)

    files.finalize(file_name)

    blob_key = files.blobstore.get_blob_key(file_name)
    logging.info('file key:%s'%blob_key)
    return blob_key

def delete_uploaded_file(k):
    logging.info('delete_uploaded_file key:"%s"'%k)
    blob_info = blobstore.BlobInfo.get(k)
    if not blob_info:
        raise Http404
    blob_info.delete()    

def response_uploaded_file(k):
    logging.info('respose_uploaded_file key:"%s"'%k)
    blob_info = blobstore.BlobInfo.get(k)
    if not blob_info:
        raise Http404
 
    blob_reader = blob_info.open()
    data = blob_reader.read()
    r =  HttpResponse(data,mimetype=blob_reader.blob_info.content_type)
    r['Content-Disposition'] = 'attachment; filename=%s'%blob_reader.blob_info.filename
    return r
