from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada
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

            user = authenticate(request, email=email, password=password, backend='app.backends.EmailBackend')

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
            return redirect('login') 

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
    template_name = 'criar_campo.html'
    login_url = '/login/'  # Redirect here if the user is not logged in

    def get(self, request, *args, **kwargs):
        form = CampoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CampoForm(request.POST)
        if form.is_valid():
            campo = form.save()  # Save the form and the object
            return redirect(self.get_success_url(campo.id))
        return render(request, self.template_name, {'form': form})

    def get_success_url(self, campo_id):
        return reverse('detalhes_campo', kwargs={'campo_id': campo_id})

# Adicionar Planta
class AdicionarPlantaNoCampoView(LoginRequiredMixin, View):
    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        form = PlantaCultivadaForm()
        return render(request, 'registrar_plantas.html', {'form': form, 'campo': campo})

    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        form = PlantaCultivadaForm(request.POST)
        if form.is_valid():
            planta_cultivada = form.save(commit=False)
            planta_cultivada.campo = campo
            planta_cultivada.save()
            return redirect('detalhes_campo', campo_id=campo.id)
        return render(request, 'registrar_plantas.html', {'form': form, 'campo': campo})


# Dá detalhes sobre o campo
class DetalhesCampoView(LoginRequiredMixin, View):
    template_name = 'detalhes_campo.html'

    def get(self, request, campo_id, *args, **kwargs):
        campo = get_object_or_404(Campo, id=campo_id)
        plantas_plantadas = PlantaCultivada.objects.filter(campo=campo)
        
        return render(request, self.template_name, {
            'campo': campo,
            'plantas_plantadas': plantas_plantadas
        })


""" REDIRECT """

class LandingView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('login')
        else:
            return redirect('login')