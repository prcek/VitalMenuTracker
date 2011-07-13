from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.data import CSVBlobReader
from google.appengine.ext.blobstore import BlobNotFoundError
from vital.models import OrderGroup,Order,OrderItem


import logging
import datetime



def getOrderGroup(order_date):
    d = datetime.date(order_date.year,order_date.month, order_date.day) 
    d_s = d - datetime.timedelta(d.weekday())

    og = OrderGroup.objects.all().filter('date =', d_s).get()
    if og is None:
        logging.info('creating new OrderGroup')
        og = OrderGroup()
        og.active = True
        og.date=d_s
        og.save()
    logging.info('order group = %s' % og)
    return og 



def index(request):

    groups = OrderGroup.objects.all().order('-date').fetch(4)
    for g in groups:
        logging.info('fetching orders for group %s'%g)
        orders = Order.objects.all().ancestor(g).order('-create_date').fetch(100)
        g.order_list=orders
        for o in g.order_list:
            logging.info('fetching items for order %s'%o)
            items = OrderItem.objects.all().ancestor(o).fetch(100)
            o.item_list = items

    return render_to_response('vital/index.html', RequestContext(request, { 'group_list': groups}))


def register_csv_order(request, file_key):
    try:
        csv = CSVBlobReader(file_key,encoding='utf-8', delimiter=';', quotechar='"')
        order_date = csv.blob_info.creation
        logging.info('registering csv order (submit date %s, key "%s")' % (order_date,file_key))
        csv.next()

        order_group = getOrderGroup(order_date)

        order = Order(parent=order_group)
        order.set_info(csv.blob_info)
        order.save()
        for row in csv:
            logging.info(row)
            for c in range(int(row[0])):
                order_item = OrderItem(parent=order)        
                if order_item.from_csv_row(row):
                    order_item.save()
                    logging.info('order item = %s'% order_item)

    except BlobNotFoundError:
        logging.info('BlobNotFoundError')
        raise Http404

    return render_to_response('vital/register_csv_order.html', RequestContext(request, { 'file_key': file_key, 'order_group': order_group }))
