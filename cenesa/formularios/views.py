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
from .forms import ExcelUploadForm
from .models import ArchivoExcel
from django.contrib import messages
from .models import ObraSocial
from .forms import ObraSocialForm



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



@login_required
@staff_member_required
def subir_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Archivo Excel subido correctamente.")
            return redirect('listar_archivos')
    else:
        form = ExcelUploadForm()

    return render(request, 'Valores/subir_excel.html', {'form': form})


@login_required
@staff_member_required
def listar_archivos(request):
    archivos = ArchivoExcel.objects.all()
    return render(request, 'Valores/listar_archivos.html', {'archivos': archivos})

@login_required
@staff_member_required
def eliminar_archivo_excel(request, id):
    archivo = get_object_or_404(ArchivoExcel, id=id)
    
    # Obtener la ruta del archivo para eliminarlo
    archivo_path = archivo.archivo.path
    
    # Asegurarse de que el archivo no esté en uso
    try:
        if os.path.exists(archivo_path):
            os.remove(archivo_path)
    except PermissionError:
        messages.error(request, "El archivo está siendo utilizado por otro proceso y no se puede eliminar.")
        return redirect('listar_archivos')
    
    # Eliminar el registro de la base de datos
    archivo.delete()
    
    # Mensaje de éxito
    messages.success(request, 'El archivo y su registro han sido eliminados correctamente.')
    
    return redirect('listar_archivos')



@login_required
@staff_member_required
def listar_obras_sociales(request):
    obras_sociales = ObraSocial.objects.all()
    return render(request, 'Valores/obra_social/listar_obras_sociales.html', {'obras_sociales': obras_sociales})

@login_required
@staff_member_required
def crear_obra_social(request):
    if request.method == 'POST':
        form = ObraSocialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra Social creada correctamente.")
            return redirect('listar_obras_sociales')
    else:
        form = ObraSocialForm()
    return render(request, 'Valores/obra_social/crear_obra_social.html', {'form': form})

@login_required
@staff_member_required
def editar_obra_social(request, id):
    obra_social = get_object_or_404(ObraSocial, id=id)
    if request.method == 'POST':
        form = ObraSocialForm(request.POST, instance=obra_social)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra Social actualizada correctamente.")
            return redirect('listar_obras_sociales')
    else:
        form = ObraSocialForm(instance=obra_social)
    return render(request, 'Valores/obra_social/editar_obra_social.html', {'form': form})

@login_required
@staff_member_required
def eliminar_obra_social(request, id):
    obra_social = get_object_or_404(ObraSocial, id=id)
    if request.method == 'POST':
        obra_social.delete()
        messages.success(request, "Obra Social eliminada correctamente.")
        return redirect('listar_obras_sociales')
    return render(request, 'Valores/obra_social/eliminar_obra_social.html', {'obra_social': obra_social})


# views.py

import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ArchivoExcel
from django.contrib import messages

def procesar_excel(request, id):
    archivo = get_object_or_404(ArchivoExcel, id=id)

    # Verificar si el archivo es un Excel
    if archivo.archivo.name.endswith('.xlsx'):
        # Leer el archivo Excel usando pandas
        excel_path = archivo.archivo.path
        xls = pd.ExcelFile(excel_path)

        # Cargar Hoja1 y Hoja2 (ajustado a tu requerimiento)
        hoja1 = pd.read_excel(xls, sheet_name='Hoja1')
        hoja2 = pd.read_excel(xls, sheet_name='Hoja2')

        # Procesamiento: Transferir datos de Hoja1 a Hoja2
        hoja1.columns = ['Practica', 'Codigo', 'Valor Pactado', 'Propuesta Valores']
        hoja1_clean = hoja1.dropna(subset=['Codigo', 'Propuesta Valores'])
        hoja1_clean['Codigo'] = pd.to_numeric(hoja1_clean['Codigo'], errors='coerce')

        hoja2['coddesde'] = pd.to_numeric(hoja2['coddesde'], errors='coerce')
        hoja2['codhasta'] = pd.to_numeric(hoja2['codhasta'], errors='coerce')

        for index, row in hoja1_clean.iterrows():
            codigo = row['Codigo']
            propuesta_valor = row['Propuesta Valores']

            hoja2.loc[(hoja2['coddesde'] <= codigo) & (hoja2['codhasta'] >= codigo), 'importe'] = propuesta_valor

        # Guardar el Excel actualizado en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=procesado_{archivo.archivo.name}'
        
        # Escribir las hojas de nuevo en el archivo de respuesta
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            hoja1.to_excel(writer, sheet_name='Hoja1', index=False)
            hoja2.to_excel(writer, sheet_name='Hoja2', index=False)

        messages.success(request, 'El archivo ha sido procesado exitosamente.')
        return response
    else:
        messages.error(request, 'El archivo no es un archivo Excel válido.')
        return redirect('listar_archivos')


# views.py

import pandas as pd
from django.http import HttpResponse
from .models import ArchivoExcel
from django.shortcuts import get_object_or_404
from io import BytesIO

def exportar_valores_procesados(request, id):
    archivo = get_object_or_404(ArchivoExcel, id=id)

    # Verificar si el archivo es un Excel
    if archivo.archivo.name.endswith('.xlsx'):
        # Leer el archivo Excel
        excel_path = archivo.archivo.path
        xls = pd.ExcelFile(excel_path)

        # Cargar Hoja1 y Hoja2
        hoja1 = pd.read_excel(xls, sheet_name='Hoja1')
        hoja2 = pd.read_excel(xls, sheet_name='Hoja2')

        # Procesar los datos (como en la vista de procesamiento)
        hoja1.columns = ['Practica', 'Codigo', 'Valor Pactado', 'Propuesta Valores']
        hoja1_clean = hoja1.dropna(subset=['Codigo', 'Propuesta Valores'])
        hoja1_clean['Codigo'] = pd.to_numeric(hoja1_clean['Codigo'], errors='coerce')

        hoja2['coddesde'] = pd.to_numeric(hoja2['coddesde'], errors='coerce')
        hoja2['codhasta'] = pd.to_numeric(hoja2['codhasta'], errors='coerce')

        for index, row in hoja1_clean.iterrows():
            codigo = row['Codigo']
            propuesta_valor = row['Propuesta Valores']

            # Asignar valores en la Hoja2
            hoja2.loc[(hoja2['coddesde'] <= codigo) & (hoja2['codhasta'] >= codigo), 'importe'] = propuesta_valor

        # Crear un buffer para almacenar el archivo Excel generado
        output = BytesIO()

        # Guardar los cambios en un archivo Excel
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            hoja1.to_excel(writer, sheet_name='Hoja1', index=False)
            hoja2.to_excel(writer, sheet_name='Hoja2', index=False)

        # Obtener el contenido del archivo Excel en memoria
        output.seek(0)

        # Enviar el archivo Excel como respuesta de descarga
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=procesado_{archivo.archivo.name}'

        return response
    else:
        # Si el archivo no es un Excel, se puede redirigir o mostrar un error
        return HttpResponse("El archivo no es un Excel válido.")
