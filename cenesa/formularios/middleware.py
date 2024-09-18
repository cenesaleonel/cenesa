from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.contrib import messages

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener todas las sesiones activas del usuario actual
            user_sessions = Session.objects.filter(expire_date__gte=now())
            previous_session = None

            for session in user_sessions:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(request.user.id) and session.session_key != request.session.session_key:
                    previous_session = session
                    session.delete()  # Eliminar la sesión anterior

            # Si había una sesión anterior, mostrar un mensaje de aviso
            if previous_session:
                messages.warning(request, 'Tenías una sesión abierta en otro dispositivo, que ha sido cerrada.')

        response = self.get_response(request)
        return response
