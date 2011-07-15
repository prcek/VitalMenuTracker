from django import forms
#from google.appengine.ext.db.djangoforms import forms
from accounts.models import Account,Transaction

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ( 'name','purpose','desc','report_email', 'report_active', 'report_in_summary' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data



class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('create_date')

    def clean_amount(self):
        data = self.cleaned_data['amount']
        if data==0:
            raise forms.ValidationError('wrong value (0)')
        return data

