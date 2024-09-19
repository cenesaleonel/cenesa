from django.http import HttpResponseForbidden

def alguna_vista(request):
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    # Lógica para usuarios admin...


