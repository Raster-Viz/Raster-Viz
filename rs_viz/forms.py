from django import forms
from .models import Layer

# basic form for creating layer objects

class LayerForm(forms.ModelForm):
    class Meta:
        model = Layer
        fields = ('name', 'document', 'activated',)
