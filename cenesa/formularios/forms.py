from django import forms
from django.forms import inlineformset_factory
from .models import Formulario, Campo

class FormularioForm(forms.ModelForm):
    class Meta:
        model = Formulario
        fields = ['nombre', 'descripcion']

CampoFormSet = inlineformset_factory(Formulario, Campo, fields=['nombre', 'tipo', 'requerido'], extra=1)
