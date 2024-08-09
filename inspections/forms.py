from django import forms
from .models import Inspection

class ImageForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['image']

class SignatureForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['signature']

class TextForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['customer_name', 'customer_id']
