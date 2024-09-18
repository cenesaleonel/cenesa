from django.db import models

class Formulario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Campo(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='campos')
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('texto', 'Texto'), ('numero', 'Número'), ('fecha', 'Fecha'), ('textarea', 'Texto Largo')])
    requerido = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
