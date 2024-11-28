from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada, Planta
from .forms import LoginForm, RegistrationForm, CampoForm, PlantaCultivadaForm




""" LOGIN / REGISTER / LOGOUT """

# Login
class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Email ou senha incorretos.')
        return render(request, self.template_name, {'form': form})

# Cadastrar
class CadastrarView(View):
    template_name = 'cadastrar.html'
    
    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.set_password(form.cleaned_data['password']) 
            user.save()
            login(request, user, backend='app.backends.EmailBackend') # Yuri te amo ♥ / Yuri rainha Gabi nadinha
            messages.success(request, f'Bem-vindo, {user.username}!') 
            return redirect('home') 

        return render(request, self.template_name, {'form': form})

# Google login
def google_login(backend, user, response, request, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = response.get('email')

        try:
            user = Agricultor.objects.get(email=email)
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            login(request, user)
        except Agricultor.DoesNotExist:
            user = Agricultor(username=email, email=email)
            user.set_unusable_password()
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            user.save()
            login(request, user)

    return {'user': user}
    
# Logout
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Você foi desconectado com sucesso.')
        return redirect(reverse_lazy('login'))

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

# Criar Campo
class CriarCampoView(LoginRequiredMixin, View):
    template_name = 'campo.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = CampoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CampoForm(request.POST)
        if form.is_valid():
            campo = form.save()
            request.user.campos.add(campo)  # Adiciona um campo para um agricultor.
            response_data = {
                'status': 'success',
                'nome': campo.nome,
                'icone': campo.icon  # Pega o ícone da form.
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors})
    
# Visualizar Campo
class VisualizarCampoView(LoginRequiredMixin, View):
    login_url = '/login/' # Se o usuário não estiver autenticado, ele volta pro login.
    
    def get(self, request):
        context = {
            "campos": request.user.get_campos(),
            "current_page" : "campos",
        }
        return render(request, "campos.html", context)

# Adicionar Planta
class AdicionarPlantaNoCampoView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        form = PlantaCultivadaForm()
        context = {
            'form': form,
            'campo': campo,
            'plantas': Planta.objects.all(),
        }
        return render(request, 'detalhes_campo.html', context)
    
    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        form = PlantaCultivadaForm(request.POST)
        if form.is_valid():
            planta_cultivada = form.save(commit=False)
            planta_cultivada.campo = campo
            planta_cultivada.save()
            response_data = {
                'status': 'success',
                'nome': planta_cultivada.planta.nome,
                'data_plantio': planta_cultivada.data_plantio,
                'quantidade_plantada': planta_cultivada.quantidade_plantada,
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors})


# Dá detalhes sobre o campo
class DetalhesCampoView(LoginRequiredMixin, View):
    
    def get(self, request, id, *args, **kwargs):
        campo = get_object_or_404(Campo, id=id, agricultor=request.user)
        plantas_cultivadas = PlantaCultivada.objects.filter(campo=campo)

        context = {
            'campo': campo,
            'lista_plantas' : Planta.objects.all(),
            'plantas_cultivadas': plantas_cultivadas,
        }

        return render(request, 'detalhes_campo.html', context)


""" Landing Route """

class LandingView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return redirect('login')

""" Home """

class HomeView(View):
    def get(self, request):
        context = {
            "user" : request.user,
            "current_page" : "home", # Colocando a página atual no contexto para o componente do footer.
        }
        return render(request, "home.html", context)
