from django.http import HttpResponse, Http404
from django import forms
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

def getExtraOrder(order_date):
    order_group = getOrderGroup(order_date)
    order = Order.objects.all().ancestor(order_group).filter('extra =',True).filter('create_date =',order_date).get()
    if order is None:
        order = Order(parent=order_group)
        order.extra=True
        order.create_date = order_date
        order.save()
        logging.info('new extra order %s'%order)
    else:
        logging.info('extra order %s'%order)
    return order 
    


def index(request):
    return render_to_response('vital/index.html', RequestContext(request, { }))


class ExtraOrderForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ( 'date','name','cost', 'undo_request' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data

    def clean_date(self):
        data = self.cleaned_data['date'] 
        if data is None:
            raise forms.ValidationError('missing value')
        return data

    def clean_cost(self):
        data = self.cleaned_data['cost']
        if data is None:
            raise forms.ValidationError('missing value')
        return data        



def extra(request):
    if request.method == 'POST':

        form = ExtraOrderForm(request.POST)
        if form.is_valid():
            date =  datetime.datetime.utcnow()
            date = datetime.datetime(date.year,date.month,date.day)
            eo = getExtraOrder(date)
            order_item = OrderItem(parent=eo)
            order_item.extra = True
            form = ExtraOrderForm(request.POST, instance=order_item)
            if form.is_valid():
                form.save(commit=False)
                logging.info('extra order item = %s',order_item)
                order_item.save()
                return redirect('/vital/')
    else:
        form = ExtraOrderForm()

    return render_to_response('vital/extra.html', RequestContext(request, { 'form': form}))


def orders(request):

    groups = OrderGroup.objects.all().order('-date').fetch(4)
    for g in groups:
        logging.info('fetching orders for group %s'%g)
        orders = Order.objects.all().ancestor(g).order('-create_date').fetch(100)
        g.order_list=orders
        for o in g.order_list:
            logging.info('fetching items for order %s'%o)
            items = OrderItem.objects.all().ancestor(o).fetch(100)
            o.item_list = items

    return render_to_response('vital/orders.html', RequestContext(request, { 'group_list': groups}))


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
            for c in range(abs(int(row[0]))):
                order_item = OrderItem(parent=order)        
                if order_item.from_csv_row(row):
                    order_item.save()
                    logging.info('order item = %s'% order_item)

    except BlobNotFoundError:
        logging.info('BlobNotFoundError')
        raise Http404

    return render_to_response('vital/register_csv_order.html', RequestContext(request, { 'file_key': file_key, 'order_group': order_group }))

def show_csv_order(request, file_key):
    try:
        csv = CSVBlobReader(file_key,encoding='utf-8', delimiter=';', quotechar='"')
        order_date = csv.blob_info.creation
        logging.info('showing csv order (submit date %s, key "%s")' % (order_date,file_key))
        list = []
        row = csv.next()
        if row:
            list.append([row,None])
        logging.info(row)
        for row in csv:
            logging.info(row)
            o = OrderItem()
            o.from_csv_row(row)
            logging.info('order item = %s'% o)
            list.append([row,o])

        cols = max([ len(r[0]) for r in list ])
        logging.info('cols = %d' % cols)
            
    except BlobNotFoundError:
        logging.info('BlobNotFoundError')
        raise Http404

    return render_to_response('vital/show_csv_order.html', RequestContext(request, { 'file_key': file_key, 'list': list, 'cols':range(cols) }))

