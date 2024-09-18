from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_formulario, name='crear_formulario'),
    path('formularios/', views.listar_formularios, name='listar_formularios'),
    path('<int:id>/ver/', views.ver_formulario, name='ver_formulario'),
    path('formularios/eliminar/<int:id>/', views.eliminar_formulario, name='eliminar_formulario'),
    
    path('solicitar/', views.solicitar_autorizacion, name='solicitar_autorizacion'),
    path('pedidos/', views.listar_pedidos_autorizacion, name='listar_pedidos_autorizacion'),
    path('pedidos/<int:id>/', views.ver_pedido_autorizacion, name='ver_pedido_autorizacion'),
    path('pedidos/aprobar/<int:id>/', views.aprobar_pedido_autorizacion, name='aprobar_pedido_autorizacion'),
    path('pedidos/rechazar/<int:id>/', views.rechazar_pedido_autorizacion, name='rechazar_pedido_autorizacion'),
    path('subir/', views.subir_pdf_rellenado, name='subir_pdf_rellenado'),
    path('pedido/eliminar/<int:id>/', views.eliminar_pedido_autorizacion, name='eliminar_pedido_autorizacion'),

    
    
    
]
