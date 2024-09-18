from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #Fromularios.
    path('formularios/', views.listar_formularios, name='listar_formularios'),
    path('formularios/crear/', views.crear_formulario, name='crear_formulario'),
    path('formularios/editar/<int:id>/', views.editar_formulario, name='editar_formulario'),
    path('formularios/rellenar/<int:id>/', views.rellenar_formulario, name='rellenar_formulario'),
    path('formularios/eliminar/<int:id>/', views.eliminar_formulario, name='eliminar_formulario'),
    
]
