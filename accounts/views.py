# Create your views here.
from accounts.models import Account,Transaction
from accounts.forms import AccountForm,TransactionForm
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext,Context, loader


import logging

def goHome(request):
    return redirect('/accounts/')

#def index(request):
#    return redirect('/accounts/show')

def account_list(request):
    account_list = Account.objects.all().fetch(100)
    return render_to_response('accounts/list.html', RequestContext(request, { 'account_list': account_list}))

def account_show(request,account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    return render_to_response('accounts/show.html', RequestContext( request, { 'account': account }))

#def update_balance(request, account_id):
#    account = Account.get_by_id(int(account_id))
#    if account is None:
#        raise Http404
#    account.updateBalance()
#    account.save()
#    return HttpResponse("OK")

def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            account = form.save(commit=False)
            account.setChange()
            account.save()
            logging.info('new account created - id: %s key: %s data: %s' % (account.key().id() , account.key(), account))
            return redirect('/accounts/')
    else:
        form = AccountForm() 
    return render_to_response('accounts/create.html', { 'form': form, 'request':request })

def account_edit(request, account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            logging.info('edit account before - id: %s key: %s data: %s' % (account.key().id() , account.key(), account))
            form.save(commit=False)
            logging.info('edit account after - id: %s key: %s data: %s' % (account.key().id() , account.key(), account))
            account.save()
            return redirect('/accounts/')
    else:
        form = AccountForm(instance=account)
    return render_to_response('accounts/edit.html', { 'form': form , 'request':request})  

def transaction_list(request, account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    transaction_list = Transaction.objects.all().ancestor(account).order('-create_date').fetch(100)
    return render_to_response('accounts/transaction_list.html', { 'request': request , 'transaction_list': transaction_list, 'account': account})

def transaction_create(request, account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
 
    if request.method == 'POST':
        t = Transaction(parent=account)
        form = TransactionForm(request.POST, instance=t)
        if form.is_valid():
            form.save(commit=False)
            t.setDate()
            t.save()
            logging.info('new transaction created - id: %s key: %s data: %s' % (t.key().id() , t.key(), t))
            return redirect('/accounts/'+account_id+'/transactions/')
    else:
        form = TransactionForm() 

    return render_to_response('accounts/transaction_create.html', { 'request': request, 'form':form })


