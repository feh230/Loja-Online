from django import forms
from django.utils.translation import gettext_lazy as _


class CouponAplayForm(forms.Form):
    code = forms.CharField(max_length=60, label=_('Coupon'))