from .models import PerfilUsuario

def agregar_tipo_usuario(request):
    if request.user.is_authenticated:
        perfil = PerfilUsuario.objects.filter(usuario=request.user).first()
        return {'tipo_usuario': perfil.tipo_usuario.nombre if perfil else None}
    return {}
