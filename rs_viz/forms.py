from django import forms
from .models import Layer

class LayerForm(forms.ModelForm):
    class Meta:
        model = Layer
        fields = ('name', 'document',)
