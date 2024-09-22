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
from .models import Novedad
from .forms import NovedadForm
from functools import wraps
from django.http import HttpResponseForbidden
from .models import PerfilUsuario

#@tipo_usuario_requerido('admin', 'editor')# Esto vamos a usar para definir las restricciones. rrhh
	#Esto son la lista  de tipo de usuarios por ahora: #facturacion #tesoreria #gerencia #personal #Farmacia #admin

def tipo_usuario_requerido(*tipos_usuarios):
    def decorator(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            # Obtener el perfil del usuario
            perfil = PerfilUsuario.objects.filter(usuario=request.user).first()
            
            # Verificar si el perfil del usuario coincide con alguno de los tipos permitidos
            if perfil and perfil.tipo_usuario.nombre in tipos_usuarios:
                return func(request, *args, **kwargs)
            else:
                # Mostrar un mensaje de error y redirigir a la página 'home'
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect('home')
        return wrap
    return decorator

# Vista Home
@login_required
def home(request):
    novedades = Novedad.objects.all().order_by('-fecha_publicacion')[:5]  # Mostrar las últimas 5 novedades
    return render(request, 'home.html', {'novedades': novedades})

@login_required
@tipo_usuario_requerido('admin', 'rrhh')
def crear_novedad(request):
    if request.method == 'POST':
        form = NovedadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirige al home donde se mostrarán las novedades
    else:
        form = NovedadForm()
    return render(request, 'novedades/crear_novedad.html', {'form': form})

# Vista para listar usuarios
@login_required
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@tipo_usuario_requerido('admin', 'rrhh')
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

@tipo_usuario_requerido('admin', 'rrhh')
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
    # Obtener el perfil del usuario para verificar su tipo
    perfil_usuario = PerfilUsuario.objects.filter(usuario=request.user).first()
    
    # Verificar si el usuario es admin o rrhh
    es_admin_o_rrhh = perfil_usuario and perfil_usuario.tipo_usuario.nombre in ['admin', 'rrhh']

    # Si es admin o rrhh, mostrar todos los pedidos, de lo contrario, solo los del usuario actual
    if es_admin_o_rrhh:
        pedidos = PedidoAutorizacion.objects.all()  # Mostrar todos los pedidos
    else:
        pedidos = PedidoAutorizacion.objects.filter(usuario=request.user)  # Mostrar solo los pedidos del usuario actual

    return render(request, 'solicitar/listar_pedidos_autorizacion.html', {'pedidos': pedidos})


@login_required
def ver_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id, usuario=request.user)
    return render(request, 'solicitar/ver_pedido_autorizacion.html', {'pedido': pedido})



@login_required
@tipo_usuario_requerido('admin', 'rrhh')
def aprobar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id)
    pedido.estado = PedidoAutorizacion.SOLICITUD_APROBADA
    pedido.save()
    return redirect('listar_pedidos_autorizacion')

@login_required
@tipo_usuario_requerido('admin', 'rrhh')
def rechazar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id)
    pedido.estado = PedidoAutorizacion.SOLICITUD_RECHAZADA
    pedido.save()
    return redirect('listar_pedidos_autorizacion')


@login_required
#NO PONER RESTRCCION YA QUE LOS USUARIOS COMUNES PUEDEN USAR ESTO #
def eliminar_pedido_autorizacion(request, id):
    pedido = get_object_or_404(PedidoAutorizacion, id=id)

    # Verificar si el usuario es el propietario del pedido o si es admin/rrhh
    es_dueno = pedido.usuario == request.user
    perfil_usuario = PerfilUsuario.objects.filter(usuario=request.user).first()
    es_admin_o_rrhh = perfil_usuario and perfil_usuario.tipo_usuario.nombre in ['admin', 'rrhh']

    # Solo permitir a admin o rrhh eliminar pedidos aprobados/rechazados
    if not es_admin_o_rrhh and pedido.estado in [PedidoAutorizacion.SOLICITUD_APROBADA, PedidoAutorizacion.SOLICITUD_RECHAZADA]:
        messages.error(request, 'No puedes eliminar un pedido que ha sido aprobado o rechazado.')
        return redirect('listar_pedidos_autorizacion')

    # Permitir que los usuarios normales solo eliminen pedidos en estado pendiente
    if es_dueno or es_admin_o_rrhh:
        if request.method == 'POST':
            # Eliminar el PDF del sistema de archivos
            if pedido.pdf_solicitud and os.path.isfile(pedido.pdf_solicitud.path):
                os.remove(pedido.pdf_solicitud.path)

            # Eliminar el pedido de autorización
            pedido.delete()
            messages.success(request, 'El pedido de autorización ha sido eliminado correctamente.')
            return redirect('listar_pedidos_autorizacion')
    else:
        messages.error(request, 'No tienes permiso para eliminar este pedido.')

    return render(request, 'solicitar/eliminar_pedido_autorizacion.html', {'pedido': pedido})

# Editar una novedad
@login_required
@tipo_usuario_requerido('admin', 'rrhh')
def editar_novedad(request, id):
    novedad = get_object_or_404(Novedad, id=id)
    if request.method == 'POST':
        form = NovedadForm(request.POST, instance=novedad)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirige al home
    else:
        form = NovedadForm(instance=novedad)
    return render(request, 'novedades/editar_novedad.html', {'form': form, 'novedad': novedad})


# Eliminar una novedad
@login_required
@tipo_usuario_requerido('admin', 'rrhh')
def eliminar_novedad(request, id):
    novedad = get_object_or_404(Novedad, id=id)
    if request.method == 'POST':
        novedad.delete()
        return redirect('home')
    return render(request, 'novedades/eliminar_novedad.html', {'novedad': novedad})


#fin de Formularios----------------------------------------------------------------------------#


#Comienzo de sector de facturacion.----------------------------------------------------------------#
@login_required
@tipo_usuario_requerido('admin', 'facturacion')
def subir_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)  # No guardes el archivo aún
            archivo.usuario = request.user  # Asigna el usuario que sube el archivo
            archivo.save()  # Ahora guarda el archivo con el usuario
            messages.success(request, "Archivo Excel subido correctamente.")
            return redirect('listar_archivos')
    else:
        form = ExcelUploadForm()

    return render(request, 'Valores/subir_excel.html', {'form': form})


from django.core.paginator import Paginator

@login_required
@tipo_usuario_requerido('admin', 'facturacion')
def listar_archivos(request):
    # Obtener los parámetros de filtrado desde la URL (si existen)
    obra_social_query = request.GET.get('obra_social', '').strip()  # Filtro por obra social
    usuario_query = request.GET.get('usuario', '').strip()  # Filtro por nombre del usuario que cargó
    fecha_query = request.GET.get('fecha', '').strip()  # Filtro por fecha de carga (formato: YYYY-MM-DD)

    # Obtener todos los archivos
    archivos = ArchivoExcel.objects.all()

    # Filtrar por obra social si se proporciona
    if obra_social_query:
        archivos = archivos.filter(obra_social__nombre__icontains=obra_social_query)

    # Filtrar por usuario si se proporciona
    if usuario_query:
        archivos = archivos.filter(usuario__username__icontains=usuario_query)

    # Filtrar por fecha si se proporciona (asumiendo formato YYYY-MM-DD)
    if fecha_query:
        archivos = archivos.filter(fecha_carga=fecha_query)

    # Paginación: 10 archivos por página
    paginator = Paginator(archivos, 10)  # Muestra 10 archivos por página
    page_number = request.GET.get('page')  # Obtener el número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener la página de archivos

    # Renderizar la vista con los resultados filtrados y paginados
    return render(request, 'Valores/listar_archivos.html', {
        'archivos': page_obj,  # Pasamos solo los archivos de la página actual
        'obra_social_query': obra_social_query,  # Mantener los filtros actuales en el contexto
        'usuario_query': usuario_query,
        'fecha_query': fecha_query,
        'page_obj': page_obj  # Información de la paginación
    })


@login_required
@tipo_usuario_requerido('admin')
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

#obra social



from django.core.paginator import Paginator
from django.contrib import messages
@login_required
@tipo_usuario_requerido('admin','facturacion')
def listar_obras_sociales(request):
    codigo_query = request.GET.get('codigo', '').strip()  # Filtro exacto por código
    nombre_query = request.GET.get('nombre', '').strip()  # Filtro parcial por nombre
    obras_sociales = ObraSocial.objects.all()

    # Filtrar por código exacto si se proporciona
    if codigo_query:
        obras_sociales = obras_sociales.filter(codigo=codigo_query)
        if not obras_sociales.exists():
            messages.warning(request, f'No se encontraron resultados para el código "{codigo_query}".')

    # Filtrar por nombre si se proporciona
    if nombre_query:
        obras_sociales = obras_sociales.filter(nombre__icontains=nombre_query)
        if not obras_sociales.exists():
            messages.warning(request, f'No se encontraron resultados para el nombre "{nombre_query}".')

    # Paginación
    paginator = Paginator(obras_sociales, 10)  # 10 resultados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Valores/obra_social/listar_obras_sociales.html', {
        'obras_sociales': page_obj,  # Enviar objetos paginados
        'codigo_query': codigo_query,  # Mantener el valor de búsqueda para el código
        'nombre_query': nombre_query,  # Mantener el valor de búsqueda para el nombre
        'page_obj': page_obj,  # Pasar la información de la página
    })


@login_required
@tipo_usuario_requerido('admin','facturacion')
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
@tipo_usuario_requerido('admin', 'facturacion')
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
@tipo_usuario_requerido('admin')
def eliminar_obra_social(request, id):
    obra_social = get_object_or_404(ObraSocial, id=id)
    if request.method == 'POST':
        obra_social.delete()
        messages.success(request, "Obra Social eliminada correctamente.")
        return redirect('listar_obras_sociales')
    return render(request, 'Valores/obra_social/eliminar_obra_social.html', {'obra_social': obra_social})



import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CargaObraSocialForm
from .models import ObraSocial
@login_required
@tipo_usuario_requerido('admin')
def carga_obra_social_geclisa(request):
    if request.method == 'POST':
        form = CargaObraSocialForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            
            # Verificar si es un archivo .xls
            if not archivo.name.endswith('.xls'):
                messages.error(request, 'El archivo debe estar en formato Excel (.xls).')
                return redirect('carga_obra_social_geclisa')

            try:
                # Leer el archivo Excel (para .xls, necesitamos 'xlrd')
                df = pd.read_excel(archivo, engine='xlrd')

                # Verificar que las columnas requeridas existan
                required_columns = ['os_cod', 'os_sigla', 'os_nombre']
                for col in required_columns:
                    if col not in df.columns:
                        messages.error(request, f"Falta la columna requerida: {col}")
                        return redirect('carga_obra_social_geclisa')

                # Procesar cada fila y guardar/actualizar en la base de datos
                for _, row in df.iterrows():
                    ObraSocial.objects.update_or_create(
                        codigo=row['os_cod'],
                        defaults={
                            'siglas': row['os_sigla'],
                            'nombre': row['os_nombre']
                        }
                    )
                messages.success(request, 'Obras sociales cargadas correctamente.')
                return redirect('listar_obras_sociales')

            except Exception as e:
                messages.error(request, f'Ocurrió un error al procesar el archivo: {e}')
                return redirect('carga_obra_social_geclisa')

    else:
        form = CargaObraSocialForm()

    return render(request, 'valores/obra_social/carga_obra_social_geclisa.html', {'form': form})


import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileForm
from .models import ObraSocial
@login_required
@tipo_usuario_requerido('admin')
def carga_obra_social_estandar(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']

            try:
                # Leer archivo Excel
                df = pd.read_excel(archivo)

                # Verificar que las columnas requeridas existan en el archivo
                required_columns = ['Codigo', 'Siglas', 'Nombre']
                for col in required_columns:
                    if col not in df.columns:
                        messages.error(request, f"El archivo Excel no contiene la columna: {col}")
                        return redirect('carga_obra_social_estandar')

                # Procesar cada fila y actualizar/crear la Obra Social
                for _, row in df.iterrows():
                    ObraSocial.objects.update_or_create(
                        codigo=row['Codigo'],
                        defaults={
                            'siglas': row['Siglas'],
                            'nombre': row['Nombre']
                        }
                    )

                messages.success(request, 'Archivo cargado y procesado con éxito.')
                return redirect('listar_obras_sociales')

            except Exception as e:
                messages.error(request, f"Ocurrió un error procesando el archivo: {str(e)}")
                return redirect('carga_obra_social_estandar')

    else:
        form = UploadFileForm()
    
    return render(request, 'Valores/obra_social/carga_obra_social_estandar.html', {'form': form})

import pandas as pd
from django.http import HttpResponse
from .models import ObraSocial
@login_required
@tipo_usuario_requerido('admin')
def exportar_obra_social_estandar(request):
    # Obtener todas las obras sociales de la base de datos
    obras_sociales = ObraSocial.objects.all()

    # Crear un DataFrame con los datos necesarios
    data = {
        'Codigo': [obra.codigo for obra in obras_sociales],
        'Siglas': [obra.siglas for obra in obras_sociales],
        'Nombre': [obra.nombre for obra in obras_sociales],
    }
    
    df = pd.DataFrame(data)

    # Crear un archivo Excel en memoria
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=obras_sociales_estandar.xlsx'

    # Escribir el DataFrame en el archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    return response




import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ArchivoExcel
from django.contrib import messages
from .models import ArchivoExcel
@login_required
@tipo_usuario_requerido('admin')
def procesar_excel(request, id):
    archivo = get_object_or_404(ArchivoExcel, id=id)

    # Verificar si el archivo ya ha sido procesado
    if archivo.procesado:
        messages.warning(request, "Este archivo ya ha sido procesado previamente.")
        return redirect('listar_archivos')

    # Verificar si el archivo es un Excel
    if archivo.archivo.name.endswith('.xlsx'):
        # Leer el archivo Excel usando pandas
        excel_path = archivo.archivo.path
        try:
            xls = pd.ExcelFile(excel_path)
        except Exception as e:
            messages.error(request, f"Error al abrir el archivo Excel: {e}")
            return redirect('listar_archivos')

        # Cargar Hoja1 y Hoja2 (o crear Hoja2 si no existe)
        try:
            hoja1 = pd.read_excel(xls, sheet_name='Hoja1')
        except Exception as e:
            messages.error(request, f"Error al leer 'Hoja1': {e}")
            return redirect('listar_archivos')

        try:
            hoja2 = pd.read_excel(xls, sheet_name='Hoja2')
        except:
            hoja2 = pd.DataFrame(columns=['coddesde', 'codhasta', 'importe'])

        # Procesar los datos y transferir de Hoja1 a Hoja2
        hoja1.columns = ['Practica', 'Codigo', 'Valor Pactado', 'Propuesta Valores']
        hoja1_clean = hoja1.dropna(subset=['Codigo', 'Propuesta Valores'])
        hoja1_clean['Codigo'] = pd.to_numeric(hoja1_clean['Codigo'], errors='coerce')
        hoja2['coddesde'] = pd.to_numeric(hoja2['coddesde'], errors='coerce')
        hoja2['codhasta'] = pd.to_numeric(hoja2['codhasta'], errors='coerce')

        for index, row in hoja1_clean.iterrows():
            codigo = row['Codigo']
            propuesta_valor = row['Propuesta Valores']
            if pd.notnull(codigo):
                hoja2.loc[(hoja2['coddesde'] <= codigo) & (hoja2['codhasta'] >= codigo), 'importe'] = propuesta_valor

        # Guardar los cambios en el archivo
        try:
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                hoja1.to_excel(writer, sheet_name='Hoja1', index=False)
                hoja2.to_excel(writer, sheet_name='Hoja2', index=False)
        except Exception as e:
            messages.error(request, f"Error al guardar el archivo Excel: {e}")
            return redirect('listar_archivos')

        # Marcar como procesado
        archivo.procesado = True
        archivo.save()

        messages.success(request, 'El archivo ha sido procesado exitosamente.')
        return redirect('listar_archivos')
    else:
        messages.error(request, 'El archivo no es un archivo Excel válido.')
        return redirect('listar_archivos') 



import pandas as pd
from django.http import HttpResponse
from .models import ArchivoExcel
from django.shortcuts import get_object_or_404
from io import BytesIO
@login_required
@tipo_usuario_requerido('admin')
def exportar_valores_procesados(request, id):
    archivo = get_object_or_404(ArchivoExcel, id=id)

    # Verificar si el archivo ha sido procesado
    if not archivo.procesado:
        messages.error(request, "No puedes exportar los valores procesados porque el archivo no ha sido procesado aún.")
        return redirect('listar_archivos')

    # Verificar si el archivo es un Excel
    if archivo.archivo.name.endswith('.xlsx'):
        # Leer el archivo Excel ya procesado
        excel_path = archivo.archivo.path
        try:
            xls = pd.ExcelFile(excel_path)
            hoja2 = pd.read_excel(xls, sheet_name='Hoja2')  # Solo necesitamos Hoja2
        except Exception as e:
            messages.error(request, f"Error al leer el archivo: {e}")
            return redirect('listar_archivos')

        # Crear un buffer para almacenar el archivo Excel generado
        output = BytesIO()

        # Guardar Hoja2 en un archivo Excel
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            hoja2.to_excel(writer, sheet_name='Hoja2', index=False)

        # Obtener el contenido del archivo Excel en memoria
        output.seek(0)

        # Enviar el archivo Excel como respuesta de descarga
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=procesado_{archivo.archivo.name}'

        return response
    else:
        messages.error(request, 'El archivo no es un archivo Excel válido.')
        return redirect('listar_archivos')
    
    
    
@login_required
@tipo_usuario_requerido('admin', 'facturacion')
def descargar_formato_excel(request):
    # Ruta completa al archivo dentro del directorio `media`
    file_path = os.path.join(settings.MEDIA_ROOT, 'formato_carga_de_valores', 'formato_de_carga.xlsx')
    
    # Verificar si el archivo existe antes de enviarlo
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='formato_de_carga.xlsx')
    else:
        # Si el archivo no está disponible, mostrar un mensaje de error y redirigir
        messages.error(request, "El archivo de formato no se encuentra disponible.")
        return redirect('listar_archivos') 
    
    
    
    
    

#-----------------------FIn proceso de facturacion ---------------------------------------------------------------------------#







 #Farmacia


import pandas as pd
from django.contrib import messages
from .models import Stock
from .forms import UploadStockForm, StockForm
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def carga_masiva_stock(request):
    if request.method == 'POST':
        form = UploadStockForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            
            # Validar que el archivo sea .xlsx
            if not archivo.name.endswith('.xlsx'):
                messages.error(request, 'El archivo debe estar en formato Excel (.xlsx).')
                return redirect('carga_masiva_stock')

            try:
                df = pd.read_excel(archivo)

                # Verificar que las columnas requeridas existan
                required_columns = ['Codigo', 'Descripccion', 'Deposito', 'Tipo de elementos', 'Cantidad']
                for col in required_columns:
                    if col not in df.columns:
                        messages.error(request, f"Falta la columna requerida: {col}")
                        return redirect('carga_masiva_stock')
                
                # Validar que la columna "Cantidad" sea numérica y no tenga valores nulos
                if df['Cantidad'].isnull().any() or not pd.api.types.is_numeric_dtype(df['Cantidad']):
                    messages.error(request, 'La columna "Cantidad" debe contener valores numéricos y no estar vacía.')
                    return redirect('carga_masiva_stock')


                # Si pasa todas las validaciones, actualizar o crear el stock
                for _, row in df.iterrows():
                    Stock.objects.update_or_create(
                        codigo=row['Codigo'],
                        defaults={
                            'descripcion': row['Descripccion'],
                            'deposito': row['Deposito'],
                            'tipo_elemento': row['Tipo de elementos'],
                            'cantidad': row['Cantidad'],
                        }
                    )

                messages.success(request, 'El archivo se cargó correctamente.')
                return redirect('listar_stock')

            except Exception as e:
                messages.error(request, f'Ocurrió un error al procesar el archivo: {e}')
                return redirect('carga_masiva_stock')
    else:
        form = UploadStockForm()
    return render(request, 'farmacia/carga_masiva_stock.html', {'form': form})


from django.core.paginator import Paginator
from django.db.models import Q
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def listar_stock(request):
    # Obtener los valores del filtro desde el request GET
    filtro_codigo = request.GET.get('codigo', '')
    filtro_descripcion = request.GET.get('descripcion', '')
    filtro_deposito = request.GET.get('deposito', '')
    filtro_tipo = request.GET.get('tipo', '')

    # Filtrar los productos usando los valores de los filtros
    stock_items = Stock.objects.all()
    
    if filtro_codigo:
        stock_items = stock_items.filter(codigo__icontains=filtro_codigo)
    if filtro_descripcion:
        stock_items = stock_items.filter(descripcion__icontains=filtro_descripcion)
    if filtro_deposito:
        stock_items = stock_items.filter(deposito__icontains=filtro_deposito)
    if filtro_tipo:
        stock_items = stock_items.filter(tipo_elemento__icontains=filtro_tipo)
    # Paginación: mostrar 20 elementos por página
    paginator = Paginator(stock_items, 20)  # 20 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtener los elementos paginados

    return render(request, 'farmacia/listar_stock.html', {
        'stock_items': page_obj,  # Usar los elementos paginados en lugar del queryset completo
        'filtro_codigo': filtro_codigo,
        'filtro_descripcion': filtro_descripcion,
        'filtro_deposito': filtro_deposito,
        'filtro_tipo': filtro_tipo,
        'page_obj': page_obj  # Pasar la información de la página para manejar la paginación en la plantilla
    })



# Vista para agregar un nuevo producto
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_stock')
    else:
        form = StockForm()
    return render(request, 'farmacia/agregar_producto.html', {'form': form})


# Vista para editar un producto existente
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def editar_producto(request, codigo):
    producto = get_object_or_404(Stock, codigo=codigo)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_stock')
    else:
        form = StockForm(instance=producto)
    return render(request, 'farmacia/editar_producto.html', {'form': form})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Stock

# Vista para eliminar un producto
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def eliminar_producto(request, codigo):
    if request.method == 'POST':
        producto = get_object_or_404(Stock, codigo=codigo)
        descripcion_producto = producto.descripcion  # Guardamos la descripción antes de eliminar
        
        # Eliminar el producto
        producto.delete()

        # Retornar respuesta JSON con éxito
        return JsonResponse({
            'success': True,
            'message': f'Producto con código {codigo} y descripción {descripcion_producto} eliminado con éxito.'
        })
    
    # Si no es una solicitud POST, retornar un error 400
    return JsonResponse({'success': False, 'message': 'Solicitud no permitida.'}, status=400)






import pandas as pd
from django.http import HttpResponse
from .models import Stock
@tipo_usuario_requerido('admin', 'Farmacia')
@login_required
def descargar_stock(request):
    # Obtener todos los productos del stock
    stock_items = Stock.objects.all()

    # Crear un DataFrame de pandas con los datos del stock
    data = {
        'Código': [item.codigo for item in stock_items],
        'Descripción': [item.descripcion for item in stock_items],
        'Depósito': [item.deposito for item in stock_items],
        'Tipo de Elemento': [item.tipo_elemento for item in stock_items],
        'Cantidad': [item.cantidad for item in stock_items],
    }
    
    df = pd.DataFrame(data)

    # Crear un archivo Excel en memoria
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=stock_actual.xlsx'
    
    # Escribir el DataFrame en el archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    return response



from django.contrib import messages
@tipo_usuario_requerido('admin')
@login_required
def volver_stock_a_cero(request):
    if request.method == 'POST':
        # Proceso de validación: preguntar al usuario si está seguro
        confirmar = request.POST.get('confirmar', 'no')
        if confirmar == 'si':
            # Validaciones adicionales pueden agregarse aquí (por ejemplo, permisos, o alguna otra validación)
            Stock.objects.all().update(cantidad=0)
            messages.success(request, 'Todo el stock ha sido puesto a 0.')
        else:
            messages.error(request, 'Acción cancelada.')
    
    return render(request, 'farmacia/confirmar_volver_stock_a_cero.html')
@tipo_usuario_requerido('admin')
@login_required
def eliminar_stock(request):
    if request.method == 'POST':
        # Proceso de validación: preguntar al usuario si está seguro
        confirmar = request.POST.get('confirmar', 'no')
        if confirmar == 'si':
            # Validaciones adicionales pueden agregarse aquí
            Stock.objects.all().delete()
            messages.success(request, 'Todo el stock ha sido eliminado.')
        else:
            messages.error(request, 'Acción cancelada.')
    
    return render(request, 'farmacia/confirmar_eliminar_stock.html')



from django.contrib import messages
from .models import Stock
from .forms import SubirArchivoExcelForm
import pandas as pd
import os
@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def actualizar_inventario(request):
    if request.method == 'POST':
        form = SubirArchivoExcelForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo_subido = form.save()
            excel_path = archivo_subido.archivo.path

            # Validar formato de archivo (.xls o .xlsx)
            if not excel_path.endswith(('.xls', '.xlsx')):
                messages.error(request, 'El archivo debe ser en formato Excel (.xls o .xlsx).')
                return redirect('actualizar_inventario')

            # Intentar leer el archivo Excel
            try:
                if excel_path.endswith('.xls'):
                    df = pd.read_excel(excel_path, engine='xlrd')
                else:
                    df = pd.read_excel(excel_path)
            except Exception as e:
                messages.error(request, f"Error al leer el archivo: {str(e)}. Asegúrese de que el archivo no esté corrupto.")
                return redirect('actualizar_inventario')

            # Validar que el archivo contenga las columnas requeridas
            required_columns = ['Código', 'Cantidad']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                messages.error(request, f"Faltan las siguientes columnas requeridas en el archivo Excel: {', '.join(missing_columns)}.")
                return redirect('actualizar_inventario')

            # Validar que la columna "Cantidad" sea numérica
            try:
                df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
                if df['Cantidad'].isnull().any():
                    raise ValueError("La columna 'Cantidad' contiene valores no numéricos o vacíos.")
            except ValueError as ve:
                messages.error(request, f"Error en la columna 'Cantidad': {ve}")
                return redirect('actualizar_inventario')

            # Procesar cambios en el inventario
            cambios_realizados = []
            errores = []

            for _, row in df.iterrows():
                try:
                    # Buscar el producto por código
                    producto = Stock.objects.get(codigo=row['Código'])
                    
                    # Verificar si hubo algún cambio en la cantidad
                    if producto.cantidad != row['Cantidad']:
                        cambios_realizados.append({
                            'producto': producto,
                            'cantidad_original': producto.cantidad,
                            'nueva_cantidad': row['Cantidad']
                        })
                        # Actualizar el stock
                        producto.cantidad = row['Cantidad']
                        producto.save()
                except Stock.DoesNotExist:
                    errores.append(f"Producto con código {row['Código']} no existe en la base de datos.")
                except KeyError as e:
                    errores.append(f"Columna faltante en el archivo Excel: {e}")
                except Exception as e:
                    errores.append(f"Error al procesar el código {row['Código']}: {str(e)}")

            # Feedback al usuario sobre los cambios realizados
            if cambios_realizados:
                messages.success(request, f"Se actualizaron {len(cambios_realizados)} productos con éxito.")
            else:
                messages.warning(request, 'No se detectaron cambios en el inventario.')

            # Informar al usuario sobre los errores encontrados
            if errores:
                for error in errores:
                    messages.error(request, error)

            # Redirigir al listado de stock
            return redirect('listar_stock')

        else:
            messages.error(request, "Por favor, corrija los errores en el formulario antes de continuar.")
    
    else:
        form = SubirArchivoExcelForm()

    return render(request, 'farmacia/actualizar_inventario.html', {'form': form})

import pandas as pd
from django.http import HttpResponse
from .models import Stock  # Asegúrate de tener el modelo correcto para el inventario
@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def descargar_inventario(request):
    # Obtener todos los productos del inventario
    stock_items = Stock.objects.all()

    # Crear un DataFrame de pandas con los datos del stock
    data = {
        'Código': [item.codigo for item in stock_items],
        'Descripción': [item.descripcion for item in stock_items],
        'Depósito': [item.deposito for item in stock_items],
        'Tipo de Elemento': [item.tipo_elemento for item in stock_items],
        'Cantidad': [item.cantidad for item in stock_items],
    }

    df = pd.DataFrame(data)

    # Crear un archivo Excel en memoria
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=inventario_actual.xlsx'

    # Escribir el DataFrame en el archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    return response


@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def descargar_estructura_excel(request):
    # Crear un DataFrame con la estructura del Excel de importación
    data = {
        'Codigo': [],
        'Descripccion': [],
        'Deposito': [],
        'Tipo de elementos': [],
        'Cantidad': []
    }

    df = pd.DataFrame(data)

    # Crear un archivo Excel en memoria
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=estructura_inventario.xlsx'

    # Escribir el DataFrame en el archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    return response


from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from django.http import HttpResponse
from .models import Stock
@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def descargar_stock_pdf(request):
    # Configurar el archivo PDF de respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="stock_actual.pdf"'

    # Crear el PDF utilizando reportlab
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    table_style = styles['BodyText']

    # Título del PDF
    elements.append(Paragraph("Listado de Stock Actual", title_style))

    # Obtener los datos del stock
    stock_items = Stock.objects.all()

    # Crear la tabla con los datos
    data = [['Código', 'Descripción', 'Depósito', 'Tipo de Elemento', 'Cantidad']]  # Encabezados

    # Agregar cada fila de datos del stock con ajuste de texto
    for item in stock_items:
        data.append([
            item.codigo,
            Paragraph(item.descripcion, table_style),  # Ajuste de texto
            item.deposito,
            item.tipo_elemento,
            item.cantidad
        ])

    # Crear la tabla y aplicar estilo
    table = Table(data, colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm, 2 * cm])

    # Estilos para la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear el texto al medio
        ('WRAP', (1, 1), (-1, -1)),  # Aplicar ajuste de texto a todo
    ]))

    # Añadir la tabla al documento
    elements.append(table)

    # Generar el PDF
    doc.build(elements)

    return response


from django.template.loader import get_template
import pdfkit # Si deseas exportar a PDF, puedes usar esta librería o una similar
from django.core.paginator import Paginator
from .models import Stock

@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def imprimir_stock(request):
    # Obtener los valores del filtro desde el request GET
    filtro_codigo = request.GET.get('codigo', '')
    filtro_descripcion = request.GET.get('descripcion', '')
    filtro_deposito = request.GET.get('deposito', '')
    filtro_tipo = request.GET.get('tipo', '')

    # Filtrar los productos usando los valores de los filtros
    stock_items = Stock.objects.all()

    if filtro_codigo:
        stock_items = stock_items.filter(codigo__icontains=filtro_codigo)
    if filtro_descripcion:
        stock_items = stock_items.filter(descripcion__icontains=filtro_descripcion)
    if filtro_deposito:
        stock_items = stock_items.filter(deposito__icontains=filtro_deposito)
    if filtro_tipo:
        stock_items = stock_items.filter(tipo_elemento__icontains=filtro_tipo)

    # Opción para mostrar en HTML o generar PDF
    if 'pdf' in request.GET:
        template = get_template('farmacia/imprimir_stock_pdf.html')
        html = template.render({'stock_items': stock_items})

        # Generar PDF usando pdfkit
        pdf = pdfkit.from_string(html, False)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="stock_filtrado.pdf"'
        return response

    # Renderizar una página para imprimir
    return render(request, 'farmacia/imprimir_stock.html', {
        'stock_items': stock_items,  # Pasar los elementos filtrados para imprimir
        'filtro_codigo': filtro_codigo,
        'filtro_descripcion': filtro_descripcion,
        'filtro_deposito': filtro_deposito,
        'filtro_tipo': filtro_tipo
    })



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Stock

# Función para modificar el stock
@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def modificar_stock(request, codigo):
    if request.method == 'POST':
        item = get_object_or_404(Stock, codigo=codigo)

        # Caso 1: Si el usuario ingresa una cantidad específica, tomarla; de lo contrario, usar 1
        cantidad_input = request.POST.get('cantidad', '')  # Intentar obtener el valor del formulario
        cantidad = int(cantidad_input) if cantidad_input else 1  # Si no hay cantidad, usar 1 por defecto

        # Almacenar la cantidad anterior antes de modificar
        cantidad_anterior = item.cantidad
        mensaje = ''

        # Caso 2: Incrementar o decrementar según la acción seleccionada
        if request.POST.get('accion') == 'incrementar':
            item.cantidad += cantidad  # Incrementar stock
            mensaje = f"Se incrementó el stock de {item.descripcion} (Código: {item.codigo}) de {cantidad_anterior} a {item.cantidad}."
        elif request.POST.get('accion') == 'decrementar':
            if item.cantidad >= cantidad:
                item.cantidad -= cantidad  # Decrementar stock si la cantidad es mayor o igual
                mensaje = f"Se restó el stock de {item.descripcion} (Código: {item.codigo}) de {cantidad_anterior} a {item.cantidad}."
            else:
                return JsonResponse({'error': 'No se puede reducir más allá de 0.'}, status=400)

        # Guardar los cambios en la base de datos
        item.save()

        # Devolver respuesta en formato JSON con los detalles
        return JsonResponse({
            'success': True,
            'nueva_cantidad': item.cantidad,
            'mensaje': mensaje,
            'codigo': item.codigo,
            'descripcion': item.descripcion,
            'cantidad_anterior': cantidad_anterior,
            'cantidad_nueva': item.cantidad
        })

    # Si no es método POST, devolver error de método no permitido
    return JsonResponse({'error': 'Método no permitido.'}, status=405)






@login_required
@tipo_usuario_requerido('admin', 'Farmacia')
def carga_formato_geclisa(request):
    if request.method == 'POST':
        form = UploadStockForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']

            # Validar que el archivo sea .xls
            if not archivo.name.endswith('.xls'):
                messages.error(request, 'El archivo debe estar en formato Excel (.xls).')
                return redirect('carga_formato_geclisa')

            try:
                # Leer el archivo .xls usando xlrd
                df = pd.read_excel(archivo, engine='xlrd')

                # Asegurarse de que las columnas requeridas existan
                required_columns = ['cant', 'ele_cod', 'ele_nombre', 'dep_nombre', 'te_nombre']
                for col in required_columns:
                    if col not in df.columns:
                        messages.error(request, f"Falta la columna requerida: {col}")
                        return redirect('carga_formato_geclisa')

                # Validar que la columna "cant" sea numérica y no tenga valores nulos
                if df['cant'].isnull().any() or not pd.api.types.is_numeric_dtype(df['cant']):
                    messages.error(request, 'La columna "cant" debe contener valores numéricos y no estar vacía.')
                    return redirect('carga_formato_geclisa')

                # Procesar cada fila del archivo y actualizar/crear el stock
                for _, row in df.iterrows():
                    Stock.objects.update_or_create(
                        codigo=row['ele_cod'],
                        defaults={
                            'descripcion': row['ele_nombre'],
                            'deposito': row['dep_nombre'],
                            'tipo_elemento': row['te_nombre'],
                            'cantidad': row['cant'],
                        }
                    )

                messages.success(request, 'El archivo Geclisa se cargó correctamente.')
                return redirect('listar_stock')

            except Exception as e:
                messages.error(request, f'Ocurrió un error al procesar el archivo: {e}')
                return redirect('carga_formato_geclisa')
    else:
        form = UploadStockForm()
    return render(request, 'farmacia/carga_formato_geclisa.html', {'form': form})
