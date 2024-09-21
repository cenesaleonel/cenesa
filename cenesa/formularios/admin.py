from django.http import HttpResponseForbidden

def alguna_vista(request):
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    # Lógica para usuarios admin...


from django.contrib import admin
from .models import TipoUsuario, PerfilUsuario

# Registrar los modelos en el administrador de Django
admin.site.register(TipoUsuario)
admin.site.register(PerfilUsuario)
