from django.http import HttpResponse, Http404
from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader

from utils.data import CSVBlobReader,store_raw_data_as_blob
from google.appengine.ext.blobstore import BlobNotFoundError
from vital.models import OrderGroup,Order,OrderItem,Clearance,ClearanceItem
from accounts.models import Account,Transaction
from utils.config import getConfig
from google.appengine.api import taskqueue



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
    date = datetime.datetime.utcnow();
    return index_day(request,date.year,date.month,date.day)

def index_day(request,year,month,day):
    date = datetime.date(int(year),int(month),int(day))
    logging.info('date=%s',date)

    next_date = date + datetime.timedelta(1)
    prev_date = date - datetime.timedelta(1)
    now_date = datetime.date.today()

    item_list = OrderItem.objects.all().filter('date = ', date).fetch(100) 
    cost_sum = 0
    for o in item_list:
        if (not o.deleted) and (not o.undo_request):
            cost_sum = cost_sum + o.cost 

    return render_to_response('vital/index.html', RequestContext(request, { 'date':date, 'next_date':next_date, 'prev_date':prev_date, 'now_date':now_date, 'item_list':item_list, 'cost_sum':cost_sum }))



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

def process_incoming_email_order(mail_message):
    logging.info('process_incoming_email_order')

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
                pass
                fk = store_raw_data_as_blob(content.decode().encode('utf-8'),name,'text/csv')
                taskqueue.add(url='/tasks/register_csv_order/%s/'%fk, method='GET')
            else:
                logging.info('no csv')
    else:
        logging.info('no attachment')


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


def clearance_index(request):
    list = Clearance.objects.all().fetch(100)

    return render_to_response('vital/clearance_index.html', RequestContext(request, {'list':list}))

def clearance_show(request, clearance_id):
    clearance = Clearance.get_by_id(int(clearance_id))
    if clearance is None:
        raise Http404

    return render_to_response('vital/clearance_show.html', RequestContext(request, {'clearance':clearance}))

class ClearanceForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today) 
    desc = forms.CharField(required=False)

class ClearanceItemPickForm(forms.Form):
    order_item_id = forms.ChoiceField()
    account_id = forms.ChoiceField()
    def __init__(self, data = None, accounts = [], order_items = []):
        super(self.__class__,self).__init__(data)
        self.fields['account_id'].choices=[(a.key(),a.as_select_string()) for a in accounts]
        self.fields['order_item_id'].choices=[(o.key(),o.as_select_string()) for o in order_items]

class ClearanceItemGiveForm(forms.Form):
    account_id = forms.ChoiceField()
    cost = forms.IntegerField()
    def __init__(self, data = None, accounts = [], cost = 0):
        super(self.__class__,self).__init__(data)
        self.fields['account_id'].choices=[(a.key(),a.as_select_string()) for a in accounts]
        self.fields['cost'].initial = cost

class ClearanceItemLoadForm(forms.Form):
    account_id = forms.ChoiceField()
    cost = forms.IntegerField()
    desc = forms.CharField(required=False)
    def __init__(self, data = None, accounts = [], cost = 0):
        super(self.__class__,self).__init__(data)
        self.fields['account_id'].choices=[(a.key(),a.as_select_string()) for a in accounts]
        self.fields['cost'].initial = cost

class ClearanceItemDepositForm(forms.Form):
    account_id = forms.ChoiceField()
    cost = forms.IntegerField()
    desc = forms.CharField(required=False)
    def __init__(self, data = None, accounts = [], cost = 0):
        super(self.__class__,self).__init__(data)
        self.fields['account_id'].choices=[(a.key(),a.as_select_string()) for a in accounts]
        self.fields['cost'].initial = cost


class ClearanceItemDelForm(forms.Form):
    item_id = forms.ChoiceField()
    def __init__(self, data = None,items = []):
        super(self.__class__,self).__init__(data)
        self.fields['item_id'].choices=[(i.key(),i.as_select_string()) for i in items]

class ClearanceItemClearForm(forms.Form):
    item_id = forms.ChoiceField()
    def __init__(self, data = None,items = []):
        super(self.__class__,self).__init__(data)
        self.fields['item_id'].choices=[(i.key(),i.as_select_string()) for i in items]


def clearance_edit(request, clearance_id):
    clearance = Clearance.get_by_id(int(clearance_id))
    if clearance is None:
        raise Http404


    if getConfig('CLEARANCE_ALL_ORDER_ITEMS',0):
        logging.info('showing all order items!')
        order_item_query = OrderItem.objects.all().filter('date =', clearance.date)
    else:
        order_item_query = OrderItem.objects.all().filter('date =', clearance.date).filter('clearance_item_ref =', None)

    c_pick_form = None
    c_give_form = None
    c_del_form = None
    c_clear_form = None
    c_load_form = None
    c_deposit_form = None

    pick_accounts = Account.objects.all().filter('purpose =', 'user').fetch(100)
    give_accounts = Account.objects.all().filter('purpose =', 'credit').fetch(100)

    if request.method == 'POST':
        logging.info(request.POST) 
        if request.POST['action'] == 'update':
            c_form = ClearanceForm(request.POST)
            if c_form.is_valid():
                clearance.date = c_form.cleaned_data['date']
                clearance.desc = c_form.cleaned_data['desc']
                clearance.save()
        if request.POST['action'] == 'pick_item':
            order_items = order_item_query.fetch(100)
            c_pick_form = ClearanceItemPickForm(request.POST,accounts=pick_accounts,order_items=order_items)     
            if c_pick_form.is_valid():
                logging.info('c_pick_form is valid!')
                order_item = OrderItem.get(c_pick_form.cleaned_data['order_item_id'])
                account = Account.get(c_pick_form.cleaned_data['account_id'])
                logging.info('account = %s'%account)
                logging.info('order_item = %s'%order_item)
                if order_item is None:
                    raise Http404
                if account is None:
                    raise Http404

                ci = ClearanceItem(parent=clearance)
                ci.account = account
                ci.order_item = order_item
                ci.cost = order_item.cost
                ci.desc = order_item.name
                ci.purpose='pick'
                ci.save()

                order_item.clearance_item_ref = ci.key()
                order_item.save() 

                c_pick_form = None

        if request.POST['action'] == 'give_item':
            c_give_form = ClearanceItemGiveForm(request.POST, give_accounts)
            if c_give_form.is_valid():
                logging.info('c_give_form is valid!')
                account = Account.get(c_give_form.cleaned_data['account_id'])
                logging.info('account = %s'%account)
                if account is None:
                    raise Http404

                ci = ClearanceItem(parent=clearance)
                ci.account = account
                ci.cost = int(c_give_form.cleaned_data['cost'])
                ci.purpose='give'
                ci.save()
  
                c_give_form = None

        if request.POST['action'] == 'load_item':
            c_load_form = ClearanceItemLoadForm(request.POST, give_accounts)
            if c_load_form.is_valid():
                logging.info('c_load_form is valid!')
                account = Account.get(c_load_form.cleaned_data['account_id'])
                logging.info('account = %s'%account)
                if account is None:
                    raise Http404

                ci = ClearanceItem(parent=clearance)
                ci.account = account
                ci.cost = int(c_load_form.cleaned_data['cost'])
                ci.purpose='load'
                ci.desc = c_load_form.cleaned_data['desc']
                ci.save()
  
                c_load_form = None

        if request.POST['action'] == 'deposit_item':
            c_deposit_form = ClearanceItemDepositForm(request.POST, pick_accounts)
            if c_deposit_form.is_valid():
                logging.info('c_deposit_form is valid!')
                account = Account.get(c_deposit_form.cleaned_data['account_id'])
                logging.info('account = %s'%account)
                if account is None:
                    raise Http404

                ci = ClearanceItem(parent=clearance)
                ci.account = account
                ci.cost = int(c_deposit_form.cleaned_data['cost'])
                ci.purpose='deposit'
                ci.desc = c_deposit_form.cleaned_data['desc']
                ci.save()
  
                c_deposit_form = None



        if request.POST['action'] == 'del_item':
            c_list = ClearanceItem.objects.all().ancestor(clearance).fetch(100)
            c_del_form = ClearanceItemDelForm(request.POST, items = c_list)
            if c_del_form.is_valid():
                logging.info('c_del_form is valid!')
                clearance_item = ClearanceItem.get(c_del_form.cleaned_data['item_id'])
                if clearance_item is None:
                    raise Http404
                if not (clearance_item.order_item is None):
                    logging.info('unmark %s'%clearance_item.order_item)
                    clearance_item.order_item.clearance_item_ref=None
                    clearance_item.order_item.save()
                clearance_item.delete()
                c_del_form = None

        if request.POST['action'] == 'clear_item':
            c_list = ClearanceItem.objects.all().ancestor(clearance).fetch(100)
            c_clear_form = ClearanceItemClearForm(request.POST, items = c_list)
            if c_clear_form.is_valid():
                logging.info('c_clear_form is valid!')
                clearance_item = ClearanceItem.get(c_clear_form.cleaned_data['item_id'])
                if clearance_item is None:
                    raise Http404
                c_clear_form = None
 

 
    
    c_form = ClearanceForm({'date':clearance.date, 'desc':clearance.desc})

    c_list = ClearanceItem.objects.all().ancestor(clearance).fetch(100)
    cost_pick = sum([i.cost for i in c_list if i.purpose=='pick'])
    cost_give = sum([i.cost for i in c_list if i.purpose=='give'])
    cost_load = sum([i.cost for i in c_list if i.purpose=='load'])
    cost_deposit = sum([i.cost for i in c_list if i.purpose=='deposit'])
 
    cost_diff = cost_pick - cost_give
    cost_put_diff = cost_deposit - cost_load
    logging.info('cost_pick=%d, cost_give=%d'%(cost_pick,cost_give))

    if c_pick_form is None:
        order_items = order_item_query.fetch(100)
        c_pick_form = ClearanceItemPickForm(accounts=pick_accounts,order_items=order_items)

    if c_give_form is None:
        c_give_form = ClearanceItemGiveForm(accounts=give_accounts,cost = cost_pick-cost_give)

    if c_del_form is None:
        c_del_form = ClearanceItemDelForm(items = c_list)

    if c_clear_form is None:
        c_clear_form = ClearanceItemClearForm(items = c_list)

    if c_load_form is None:
        c_load_form = ClearanceItemLoadForm(accounts=give_accounts, cost = cost_put_diff)
    
    if c_deposit_form is None:
        c_deposit_form = ClearanceItemDepositForm(accounts=pick_accounts)





    return render_to_response('vital/clearance_edit.html', RequestContext(request, 
            {'c_form':c_form, 'c_list':c_list, 'c_pick_form': c_pick_form, 'c_give_form': c_give_form, 'c_del_form':c_del_form, 
             'cost_pick':cost_pick, 'cost_give':cost_give, 'cost_diff':cost_diff, 'c_clear_form':c_clear_form,
             'c_load_form':c_load_form, 'c_deposit_form':c_deposit_form,
             'cost_load':cost_load, 'cost_deposit':cost_deposit, 'cost_put_diff':cost_put_diff,
            }))

   

def clearance_create(request):
    if request.method == 'POST':
        form = ClearanceForm(request.POST)
        if form.is_valid():
            c = Clearance()
            c.date = form.cleaned_data['date']
            c.desc = form.cleaned_data['desc']
            c.save()
            return redirect('/vital/clearance/%d/edit/'%c.key().id())
    else: 
        form = ClearanceForm()

    return render_to_response('vital/clearance_create.html', RequestContext(request, {'form':form}))

def clearance_commit(request, clearance_id):
    clearance = Clearance.get_by_id(int(clearance_id))
    if clearance is None:
        raise Http404

    logging.info('clearance=%s'%clearance)

    if clearance.lock:
        info = 'clearance is locked!'
    else:
        clearance.lock = True
        clearance.save()
        logging.info('add task for "do_clearance(%d)"' % clearance.key().id())
        taskqueue.add(url='/tasks/do_clearance/%s/'%clearance.key().id(), method='GET')
        info = 'task add ok'
    

    return render_to_response('vital/clearance_commit.html', RequestContext(request, {'clearance':clearance, 'info':info}))


def task_do_clearance(request, clearance_id):
    logging.info('task do clearance - clearance_id=%s'%clearance_id)
    clearance = Clearance.get_by_id(int(clearance_id))
    if clearance is None:
        raise Http404

    logging.info('clearance = %s'%clearance)


         
    items = ClearanceItem.objects.all().ancestor(clearance)
    for i in items:
        logging.info('i=%s'%i) 
        if not (i.transaction_item is None):
            logging.info('has transaction...')
            if not i.clear:
                logging.info('but,not clear...')
                i.clear = True
                i.save()
                logging.info('cleared')
        else:
            tr = Transaction.objects.all().filter('clearance_item_key =', i.key()).get()
            if not (tr is None):
                logging.info('corresponding transaction found (%s)'%tr)
                i.transaction_item=tr
                logging.info('linked')
            else:
                logging.info('no corresponding transaction found')
                tr = Transaction(parent=i.account)
                tr.setDate()
                tr.clearance_item_key = i.key()
                if i.purpose == 'pick':
                    logging.info('pick item')
                    tr.purpose = 'payment'
                    tr.order_item_key = i.order_item.key()
                    tr.amount = -i.cost
                    tr.desc = i.desc
                elif i.purpose == 'give':
                    logging.info('give item')
                    tr.purpose = 'payment'
                    tr.amount = -i.cost
                    tr.desc = i.desc
                elif i.purpose == 'deposit':  
                    logging.info('deposit item')
                    tr.purpose = 'deposit'
                    tr.amount = i.cost
                    tr.desc = i.desc
                elif i.purpose == 'load':
                    logging.info('load item')
                    tr.purpose = 'deposit'
                    tr.amount = i.cost
                    tr.desc = i.desc
                else:
                    logging.info('unexpected purpose (%s)'%i.purpose)
                    tr = None

                logging.info('new tr=%s'%tr)
                if not (tr is None):
                    tr.save()
                    logging.info('tr save ok %s'%tr) 
                    i.transaction_item = tr
                    i.clear = True
                
            i.save()    
            logging.info('new tr=%s'%tr)
                


    logging.info('unlock clearance') 
    clearance.status = 'closed'
    clearance.lock = False
    clearance.clear = True
    clearance.save()

    return HttpResponse('ok')


