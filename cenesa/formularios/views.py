from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from django.http import FileResponse
from .models import Formulario, PedidoAutorizacion
from .forms import FormularioForm, PedidoAutorizacionForm
import os
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import datetime
# Vista Home
@login_required
def home(request):
    return render(request, 'home.html')

# Vista para listar usuarios
@login_required
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_formulario(request):
    if request.method == 'POST':
        form = FormularioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_formularios')
    else:
        form = FormularioForm()
    return render(request, 'formularios/crear_formulario.html', {'form': form})

@login_required
def listar_formularios(request):
    formularios = Formulario.objects.all()
    return render(request, 'formularios/listar_formularios.html', {'formularios': formularios})

@login_required
def ver_formulario(request, id):
    formulario = get_object_or_404(Formulario, id=id)
    return render(request, 'formularios/ver_formulario.html', {'formulario': formulario})

@login_required
def eliminar_formulario(request, id):
    formulario = get_object_or_404(Formulario, id=id)
    if request.method == 'POST':
        formulario.delete()
        return redirect('listar_formularios')
    return render(request, 'formularios/eliminar_formulario.html', {'formulario': formulario})

@login_required
def solicitar_autorizacion(request):
    formularios = Formulario.objects.all()  # Formularios disponibles

    if request.method == 'POST':
        pdf_id = request.POST.get('formulario_id')  # Obtener el PDF seleccionado
        formulario_seleccionado = get_object_or_404(Formulario, id=pdf_id)

        # Obtener la ruta del PDF seleccionado
        pdf_path = formulario_seleccionado.pdf.path

        # Crear una respuesta de archivo para descargar el PDF
        try:
            response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{formulario_seleccionado.nombre}.pdf"'
            return response  # Se descarga el PDF seleccionado
        except FileNotFoundError:
            # Manejar el error si el archivo no existe
            return render(request, 'error.html', {'mensaje': 'El archivo no fue encontrado.'})

    else:
        return render(request, 'solicitar/solicitar_autorizacion.html', {
            'formularios': formularios,
        })

@login_required
def subir_pdf_rellenado(request):
    if request.method == 'POST':
        form = PedidoAutorizacionForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.nombre_solicitante = f'{request.user.first_name} {request.user.last_name}'
            pedido.estado = PedidoAutorizacion.SOLICITUD_PENDIENTE
            pedido.save()
            return redirect('listar_pedidos_autorizacion')
    else:
        form = PedidoAutorizacionForm()
    return render(request, 'solicitar/subir_pdf_rellenado.html', {'form': form})


@login_required
def listar_pedidos_autorizacion(request):
    # Si el usuario es staff, muestra todos los pedidos, de lo contrario, solo los del usuario actual
    if request.user.is_staff:
        pedidos = PedidoAutorizacion.objects.all()  # Mostrar todos los pedidos
    else:
        pedidos = PedidoAutorizacion.objects.filter(usuario=request.user)  # Mostrar solo los pedidos del usuario actual

    return render(request, 'solicitar/listar_pedidos_autorizacion.html', {'pedidos': pedidos})


@login_required
def ver_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id, usuario=request.user)
    return render(request, 'solicitar/ver_pedido_autorizacion.html', {'pedido': pedido})



@login_required
@staff_member_required
def aprobar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id)
    pedido.estado = PedidoAutorizacion.SOLICITUD_APROBADA
    pedido.save()
    return redirect('listar_pedidos_autorizacion')

@login_required
@staff_member_required
def rechazar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id)
    pedido.estado = PedidoAutorizacion.SOLICITUD_RECHAZADA
    pedido.save()
    return redirect('listar_pedidos_autorizacion')


@login_required
@staff_member_required
def eliminar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id, usuario=request.user)
    
    if request.method == 'POST':
        # Eliminar el PDF del sistema de archivos
        if pedido.pdf_solicitud and os.path.isfile(pedido.pdf_solicitud.path):
            os.remove(pedido.pdf_solicitud.path)
        
        # Eliminar el pedido de autorización
        pedido.delete()
        
        return redirect('listar_pedidos_autorizacion')

    return render(request, 'solicitar/eliminar_pedido_autorizacion.html', {'pedido': pedido})
