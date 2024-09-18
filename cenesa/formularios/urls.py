from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_formulario, name='crear_formulario'),
    path('formularios/', views.listar_formularios, name='listar_formularios'),
    path('<int:id>/ver/', views.ver_formulario, name='ver_formulario'),
    path('formularios/eliminar/<int:id>/', views.eliminar_formulario, name='eliminar_formulario'),
]
