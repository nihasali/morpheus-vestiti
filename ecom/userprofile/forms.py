from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['fullname','phone','address','city','state','zipcode','landmark','default']