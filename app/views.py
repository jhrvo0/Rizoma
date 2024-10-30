from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada, Planta, Evento
from .forms import LoginForm, RegistrationForm, CampoForm, PlantaCultivadaForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import date, datetime, timedelta




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
        
# Deletar Campo
class DeletarCampoView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        campo.delete()
        return redirect('campos')
    
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

class DeletarPlantaView(LoginRequiredMixin, View):
    def post(self, request, planta_id):
        planta = get_object_or_404(PlantaCultivada, id=planta_id)
        campo_id = planta.campo.id
        planta.delete()
        messages.success(request, 'Planta deletada com sucesso.')
        return redirect('detalhes-campo', campo_id=campo_id)

# Dá detalhes sobre o campo
class DetalhesCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        plantas_cultivadas = PlantaCultivada.objects.filter(campo=campo)
        context = {
            'campo': campo,
            'plantas_cultivadas': plantas_cultivadas,
            'plantas': Planta.objects.all(),  # Adicione as plantas ao contexto
        }
        return render(request, 'detalhes_campo.html', context)

    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        nome = request.POST.get('nome')
        if nome:
            campo.nome = nome
            campo.save()
            messages.success(request, 'Nome do campo atualizado com sucesso.')
        return redirect('detalhes-campo', campo_id=campo_id)


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
            "user": request.user,
            "current_page": "home",
        }
        return render(request, "home.html", context)

class CalendarioView(View):
    def get(self, request):
        eventos = list(Evento.objects.values())
        for evento in eventos:
            evento['data_inicio'] = evento['data_inicio'].strftime('%Y-%m-%d')
            if evento['data_fim']:
                evento['data_fim'] = evento['data_fim'].strftime('%Y-%m-%d')
        context = {
            "eventos": json.dumps(eventos),
            "current_page": "calendario",
        }
        return render(request, 'calendario.html', context)

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            descricao = data.get('descricao')
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
            cor = data.get('cor', '#FF5733')

            evento = Evento.objects.create(
                descricao=descricao,
                data_inicio=data_inicio,
                data_fim=data_fim,
                cor=cor
            )
            return JsonResponse({"status": "success", "evento_id": evento.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    @method_decorator(csrf_exempt)
    def delete(self, request, evento_id):
        try:
            evento = get_object_or_404(Evento, id=evento_id)
            single_day = request.GET.get('single_day') == 'true'
            date = request.GET.get('date')
            if single_day and date:
                # Convert the date string to a date object
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                
                # If the event starts and ends on the same day, delete it
                if evento.data_inicio == evento.data_fim:
                    evento.delete()
                # If the event starts on the date to be removed, move the start date to the next day
                elif evento.data_inicio == date_obj:
                    evento.data_inicio = date_obj + timedelta(days=1)
                    evento.save()
                # If the event ends on the date to be removed, move the end date to the previous day
                elif evento.data_fim == date_obj:
                    evento.data_fim = date_obj - timedelta(days=1)
                    evento.save()
                # If the event spans the date to be removed, split the event into two
                else:
                    Evento.objects.create(
                        descricao=evento.descricao,
                        data_inicio=date_obj + timedelta(days=1),
                        data_fim=evento.data_fim,
                        cor=evento.cor
                    )
                    evento.data_fim = date_obj - timedelta(days=1)
                    evento.save()
            else:
                evento.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
