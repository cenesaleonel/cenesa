from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm 
from .models import Formulario
from .forms import FormularioForm


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