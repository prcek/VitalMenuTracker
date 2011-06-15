from django import forms
#from google.appengine.ext.db.djangoforms import forms
from accounts.models import Account

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ( 'name','desc' )

    def clean_name(self):
        data = self.cleaned_data['name']
        if len(data)==0:
            raise forms.ValidationError('missing value')
        return data
