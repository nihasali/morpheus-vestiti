from django import forms
from .models import Coupon

class CouponCreateForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ["code", "discount_value", "min_purchase_amount", "valid_from", "valid_to", "active", "usage_limit"]

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        if Coupon.objects.filter(code__iexact=code).exists():
            raise forms.ValidationError('coupon already exists!.')
        return code

    def clean_discount_value(self):
        discount = self.cleaned_data.get('discount_value')
        if discount <= 0:
            raise forms.ValidationError("Discount value must be greater than zero.")
        if discount > 80:
            raise forms.ValidationError("Discount cannot exceed 80%.")
        return discount

    def clean_min_purchase_amount(self):
        min_purchase = self.cleaned_data.get('min_purchase_amount')
        if min_purchase < 0:
            raise forms.ValidationError("Minimum purchase amount cannot be negative.")
        return min_purchase
