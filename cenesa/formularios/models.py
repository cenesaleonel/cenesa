from django.db import models
import os
from PyPDF2 import PdfReader, PdfWriter
from django.conf import settings
from django.contrib.auth.models import User


class Formulario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)  
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    def delete(self, *args, **kwargs):
        if self.pdf:
            if os.path.isfile(self.pdf.path):
                os.remove(self.pdf.path)  # Elimina el archivo físico
        super().delete(*args, **kwargs)  # Llama al método delete original para eliminar el registro de la BD


class Campo(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='campos')
    nombre = models.CharField(max_length=255)  # Nombre del campo dinámico
    etiqueta = models.CharField(max_length=255)  # Etiqueta para mostrar en el formulario
    tipo = models.CharField(max_length=50, choices=[('texto', 'Texto'), ('numero', 'Número'), ('fecha', 'Fecha'), ('textarea', 'Texto Largo')])  # Tipos de campo disponibles
    requerido = models.BooleanField(default=True)  # Indica si el campo es obligatorio o no

    def __str__(self):
        return self.nombre



class PedidoAutorizacion(models.Model):
    SOLICITUD_PENDIENTE = 'pendiente'
    SOLICITUD_APROBADA = 'aprobada'
    SOLICITUD_RECHAZADA = 'rechazada'
    ESTADO_CHOICES = [
        (SOLICITUD_PENDIENTE, 'Pendiente'),
        (SOLICITUD_APROBADA, 'Aprobada'),
        (SOLICITUD_RECHAZADA, 'Rechazada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)# Vincula con el usuario autenticado
    nombre_solicitante = models.CharField(max_length=255)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    pdf_solicitud = models.FileField(upload_to='pdf/solicitudes/')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=SOLICITUD_PENDIENTE)
    comentarios = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.nombre_solicitante} - {self.fecha_solicitud}'


#Para los valores 
class ObraSocial(models.Model):
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

# carga de excel
class ArchivoExcel(models.Model):
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE, related_name="archivos")
    archivo = models.FileField(upload_to='media/excel')
    fecha_carga = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Archivo {self.archivo.name} - {self.obra_social.nombre} ({self.fecha_carga})"
    

class Novedad(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    fecha_publicacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titulo




class Stock(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)
    deposito = models.CharField(max_length=255)
    tipo_elemento = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.descripcion} ({self.cantidad})"





class ArchivoExcelSubido(models.Model):
    archivo = models.FileField(upload_to='archivos_subidos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

