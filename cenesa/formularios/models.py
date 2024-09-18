from django.db import models
import os

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
