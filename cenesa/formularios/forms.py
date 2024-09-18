from django import forms
from .models import PedidoAutorizacion, Formulario

class FormularioForm(forms.ModelForm):
    class Meta:
        model = Formulario
        fields = ['nombre', 'descripcion', 'pdf']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del formulario'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del formulario'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class PedidoAutorizacionForm(forms.ModelForm):
    class Meta:
        model = PedidoAutorizacion
        fields = ['comentarios', 'pdf_solicitud']
        widgets = {
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'pdf_solicitud': forms.FileInput(attrs={'class': 'form-control'}),
        }

# forms.py

class FormularioDeEdicion(forms.Form):
    # Define aquí los campos que corresponden a los campos del PDF
    nombre = forms.CharField(label='Nombre', max_length=100)
    fecha = forms.DateField(label='Fecha')
    comentarios = forms.CharField(widget=forms.Textarea, required=False)