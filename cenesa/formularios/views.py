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


# Vista Home
@login_required
def home(request):
    novedades = Novedad.objects.all().order_by('-fecha_publicacion')[:5]  # Mostrar las últimas 5 novedades
    return render(request, 'home.html', {'novedades': novedades})

@login_required
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

@login_required
@staff_member_required
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



import pandas as pd
from django.http import HttpResponse
from .models import ArchivoExcel
from django.shortcuts import get_object_or_404
from io import BytesIO
@login_required
@staff_member_required
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





# Editar una novedad
@login_required
@staff_member_required
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
@staff_member_required
def eliminar_novedad(request, id):
    novedad = get_object_or_404(Novedad, id=id)
    if request.method == 'POST':
        novedad.delete()
        return redirect('home')
    return render(request, 'novedades/eliminar_novedad.html', {'novedad': novedad})



 #Farmacia


import pandas as pd
from django.contrib import messages
from .models import Stock
from .forms import UploadStockForm, StockForm


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

                # Verificar que no haya códigos duplicados en el archivo
                if df['Codigo'].duplicated().any():
                    messages.error(request, 'El archivo contiene códigos de productos duplicados.')
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


from django.db.models import Q

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

    return render(request, 'farmacia/listar_stock.html', {
        'stock_items': stock_items,
        'filtro_codigo': filtro_codigo,
        'filtro_descripcion': filtro_descripcion,
        'filtro_deposito': filtro_deposito,
        'filtro_tipo': filtro_tipo
    })


# Vista para agregar un nuevo producto
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


# Vista para eliminar un producto
def eliminar_producto(request, codigo):
    producto = get_object_or_404(Stock, codigo=codigo)
    producto.delete()
    return redirect('listar_stock')


import pandas as pd
from django.http import HttpResponse
from .models import Stock

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
def actualizar_inventario(request):
    if request.method == 'POST':
        form = SubirArchivoExcelForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo_subido = form.save()

            # Leer el archivo Excel subido
            excel_path = archivo_subido.archivo.path
            df = pd.read_excel(excel_path)

            # Validar si el archivo contiene cambios
            cambios_realizados = []
            errores = []
            for _, row in df.iterrows():
                try:
                    # Buscar el producto por código
                    producto = Stock.objects.get(codigo=row['Código'])
                    
                    # Verificar si hubo algún cambio en las cantidades
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
                    errores.append(f"Producto con código {row['Código']} no existe.")
                except KeyError as e:
                    errores.append(f"Columna faltante en el archivo Excel: {e}")

            # Si no hubo cambios
            if not cambios_realizados:
                messages.warning(request, 'No se detectaron cambios en el archivo Excel.')
            else:
                messages.success(request, f"Se actualizaron {len(cambios_realizados)} productos.")
            
            # Reportar errores
            if errores:
                for error in errores:
                    messages.error(request, error)

            return redirect('listar_stock')
    
    else:
        form = SubirArchivoExcelForm()

    return render(request, 'farmacia/actualizar_inventario.html', {'form': form})

import pandas as pd
from django.http import HttpResponse
from .models import Stock  # Asegúrate de tener el modelo correcto para el inventario

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



def descargar_estructura_excel(request):
    # Crear un DataFrame con la estructura del Excel de importación
    data = {
        'Código': [],
        'Descripción': [],
        'Depósito': [],
        'Tipo de Elemento': [],
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