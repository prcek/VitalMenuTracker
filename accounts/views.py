# Create your views here.
from accounts.models import Account
from accounts.forms import AccountForm
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import Context, loader


import logging

def goHome(request):
    return redirect('/accounts/show')

def index(request):
    return redirect('/accounts/show')

def show_all(request):
    account_list = Account.objects.all().fetch(10)
    t = loader.get_template('accounts/show_all.html')
    c = Context({'account_list': account_list,'request':request})
    return HttpResponse(t.render(c))

def show_account(request,account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    t = loader.get_template('accounts/show_account.html')
    c = Context({'account': account, 'request':request})
    return HttpResponse(t.render(c))

def update_balance(request, account_id):
    account = Account.get_by_id(int(account_id))
    if account is None:
        raise Http404
    account.updateBalance()
    account.save()
    return HttpResponse("OK")

def create_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            logging.info('form data' + form.cleaned_data['name'])
            account = form.save(commit=False)
            account.setChange()
            account.save()
            logging.info('new account created - id: %s key: %s data: %s' % (account.key().id() , account.key(), account))
            return redirect('/accounts/show')
    else:
        form = AccountForm() 
    return render_to_response('accounts/create_account.html', { 'form': form, 'request':request })

def edit_account(request, account_id):
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
            return redirect('/accounts/show')
    else:
        form = AccountForm(instance=account)
    return render_to_response('accounts/edit_account.html', { 'form': form , 'request':request})  

