from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
from django.http import HttpResponse, Http404
import csv,codecs,cStringIO
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

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        orow = []
        for s in row:
            if 'encode' in dir(s):
                orow.append(s.encode("utf-8"))
            else:
                orow.append(s)
            
        self.writer.writerow(orow)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def dump_to_csv(query,out):
    wr = UnicodeWriter(out,delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)        
    for obj in query:
        logging.info(obj.as_csv_row())
        wr.writerow(obj.as_csv_row())
 

