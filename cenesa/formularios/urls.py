from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_formulario, name='crear_formulario'),
    path('formularios/', views.listar_formularios, name='listar_formularios'),
    path('<int:id>/ver/', views.ver_formulario, name='ver_formulario'),
    path('formularios/eliminar/<int:id>/', views.eliminar_formulario, name='eliminar_formulario'),
    path('crear-novedad/', views.crear_novedad, name='crear_novedad'),
    path('editar-novedad/<int:id>/', views.editar_novedad, name='editar_novedad'),
    path('eliminar-novedad/<int:id>/', views.eliminar_novedad, name='eliminar_novedad'),
    
    path('solicitar/', views.solicitar_autorizacion, name='solicitar_autorizacion'),
    path('pedidos/', views.listar_pedidos_autorizacion, name='listar_pedidos_autorizacion'),
    path('pedidos/<int:id>/', views.ver_pedido_autorizacion, name='ver_pedido_autorizacion'),
    path('pedidos/aprobar/<int:id>/', views.aprobar_pedido_autorizacion, name='aprobar_pedido_autorizacion'),
    path('pedidos/rechazar/<int:id>/', views.rechazar_pedido_autorizacion, name='rechazar_pedido_autorizacion'),
    path('subir/', views.subir_pdf_rellenado, name='subir_pdf_rellenado'),
    path('pedido/eliminar/<int:id>/', views.eliminar_pedido_autorizacion, name='eliminar_pedido_autorizacion'),

    path('subir-excel/', views.subir_excel, name='subir_excel'),
    path('listar-archivos/', views.listar_archivos, name='listar_archivos'),
    path('exportar-valores-procesados/<int:id>/', views.exportar_valores_procesados, name='exportar_valores_procesados'),
    path('procesar-excel/<int:id>/', views.procesar_excel, name='procesar_excel'),
    path('eliminar-archivo/<int:id>/', views.eliminar_archivo_excel, name='eliminar_archivo_excel'),
    
    
    path('obras-sociales/', views.listar_obras_sociales, name='listar_obras_sociales'),
    path('obras-sociales/crear/', views.crear_obra_social, name='crear_obra_social'),
    path('obras-sociales/editar/<int:id>/', views.editar_obra_social, name='editar_obra_social'),
    path('obras-sociales/eliminar/<int:id>/', views.eliminar_obra_social, name='eliminar_obra_social'),
    
    path('carga-masiva/', views.carga_masiva_stock, name='carga_masiva_stock'),
    path('listar-stock/', views.listar_stock, name='listar_stock'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('editar-producto/<str:codigo>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<str:codigo>/', views.eliminar_producto, name='eliminar_producto'),
    
]
