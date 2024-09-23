from django.urls import path
from . import views
from .views import carga_obra_social_geclisa , carga_obra_social_estandar , exportar_obra_social_estandar, descargar_formato_excel, modificar_stock_minimo

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
    path('descargar-formato/', descargar_formato_excel, name='descargar_formato_excel'),
    
    
    path('obras-sociales/', views.listar_obras_sociales, name='listar_obras_sociales'),
    path('obras-sociales/crear/', views.crear_obra_social, name='crear_obra_social'),
    path('obras-sociales/editar/<int:id>/', views.editar_obra_social, name='editar_obra_social'),
    path('obras-sociales/eliminar/<int:id>/', views.eliminar_obra_social, name='eliminar_obra_social'),
    path('carga-obra-social-geclisa/', carga_obra_social_geclisa, name='carga_obra_social_geclisa'),
    path('carga-obra-social-estandar/', carga_obra_social_estandar, name='carga_obra_social_estandar'),
    path('exportar-obra-social-estandar/', exportar_obra_social_estandar, name='exportar_obra_social_estandar'),
    path('vaciar-obras-sociales/', views.vaciar_obras_sociales, name='vaciar_obras_sociales'),
    


    
    path('carga-masiva/', views.carga_masiva_stock, name='carga_masiva_stock'),
    path('listar-stock/', views.listar_stock, name='listar_stock'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('editar-producto/<str:codigo>/', views.editar_producto, name='editar_producto'),
    path('descargar-stock/', views.descargar_stock, name='descargar_stock'),
    path('volver-stock-cero/', views.volver_stock_a_cero, name='volver_stock_a_cero'),
    path('eliminar-stock/', views.eliminar_stock, name='eliminar_stock'),
    path('actualizar-inventario/', views.actualizar_inventario, name='actualizar_inventario'),
    path('descargar-inventario/', views.descargar_inventario, name='descargar_inventario'),
    path('descargar-estructura-excel/', views.descargar_estructura_excel, name='descargar_estructura_excel'),
    path('modificar-stock/<str:codigo>/', views.modificar_stock, name='modificar_stock'),
    path('carga-formato-geclisa/', views.carga_formato_geclisa, name='carga_formato_geclisa'),
    path('descargar-stock-pdf/', views.descargar_stock_pdf, name='descargar_stock_pdf'),
    path('eliminar-producto/<str:codigo>/', views.eliminar_producto, name='eliminar_producto'),
    path('imprimir-stock/', views.imprimir_stock, name='imprimir_stock'),
    path('modificar-stock-minimo/<str:codigo>/', views.modificar_stock_minimo, name='modificar_stock_minimo'),
]
