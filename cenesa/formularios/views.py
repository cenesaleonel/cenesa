from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Formulario, Campo
from .forms import FormularioForm, CampoFormSet

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
        form = FormularioForm(request.POST)
        campo_formset = CampoFormSet(request.POST)
        if form.is_valid() and campo_formset.is_valid():
            formulario = form.save()
            campos = campo_formset.save(commit=False)
            for campo in campos:
                campo.formulario = formulario
                campo.save()
            return redirect('listar_formularios')
    else:
        form = FormularioForm()
        campo_formset = CampoFormSet()
    return render(request, 'formularios/crear_formulario.html', {'form': form, 'campo_formset': campo_formset})

@login_required
def rellenar_formulario(request, id):
    formulario = Formulario.objects.get(id=id)
    if request.method == 'POST':
        # Guardar la información rellenada
        pass
    return render(request, 'formularios/rellenar_formulario.html', {'formulario': formulario})
