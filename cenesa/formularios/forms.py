from django import forms
from .models import PedidoAutorizacion, Formulario ,  Novedad
from .models import ObraSocial

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



from .models import ArchivoExcel

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ArchivoExcel
        fields = ['obra_social', 'archivo']
        widgets = {
            'obra_social': forms.Select(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




class ObraSocialForm(forms.ModelForm):
    class Meta:
        model = ObraSocial
        fields = ['nombre', 'codigo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Obra Social'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
        }
        
 


class CargaObraSocialForm(forms.Form):
    archivo_excel = forms.FileField(label='Archivo Excel para cargar Obras Sociales Geclisa') 
        
class NovedadForm(forms.ModelForm):
    class Meta:
        model = Novedad
        fields = ['titulo', 'contenido']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la novedad'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenido de la novedad'}),
        }        

class UploadFileForm(forms.Form):
    archivo_excel = forms.FileField(label="Selecciona un archivo Excel")

from django import forms
from .models import Stock

class UploadStockForm(forms.Form):
    archivo_excel = forms.FileField()

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['codigo', 'descripcion', 'deposito', 'tipo_elemento', 'cantidad']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'deposito': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_elemento': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    
    

from django import forms
from .models import ArchivoExcelSubido
class SubirArchivoExcelForm(forms.ModelForm):
    class Meta:
        model = ArchivoExcelSubido
        fields = ['archivo']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    
    


class UploadStockForm(forms.Form):
    archivo_excel = forms.FileField(
        label="Selecciona un archivo Excel (.xls o .xlsx)",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
