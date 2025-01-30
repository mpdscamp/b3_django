# assets/forms.py

from django import forms
from .models import Asset, PriceTunnel, Frequency, AvailableAsset
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class AssetForm(forms.ModelForm):
    """
    Create or update an Asset by choosing from a list of AvailableAsset.
    """
    class Meta:
        model = Asset
        fields = ['available_asset']  # The user picks from your master list

class PriceTunnelForm(forms.ModelForm):
    class Meta:
        model = PriceTunnel
        fields = ['lower_limit', 'upper_limit']

    def clean(self):
        cleaned_data = super().clean()
        lower_limit = cleaned_data.get('lower_limit')
        upper_limit = cleaned_data.get('upper_limit')

        if lower_limit is not None and upper_limit is not None:
            if lower_limit >= upper_limit:
                raise ValidationError(
                    "The upper limit must be greater than the lower limit."
                )
            if lower_limit < 0:
                raise ValidationError(
                    "The lower limit cannot be negative."
                )

        return cleaned_data

class FrequencyForm(forms.ModelForm):
    class Meta:
        model = Frequency
        fields = ['interval_minutes']

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Username or password is incorrect.',
        'inactive': 'This account is inactive.',
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data