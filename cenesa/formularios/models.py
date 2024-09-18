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
