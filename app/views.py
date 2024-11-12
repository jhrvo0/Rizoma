from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada, Planta, Evento
from .forms import LoginForm, RegistrationForm, CampoForm, PlantaCultivadaForm, ProfileForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import date, datetime, timedelta
from django.template.loader import render_to_string





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
    if (backend.name == 'google-oauth2'):
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
    
    def Filtrar_campos(request):
        if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            nome = request.GET.get("nome", "")
            sort = request.GET.get("sort", "az")  # Parâmetro de ordenação
            campos = Campo.objects.all()
            if nome:
                campos = campos.filter(nome__icontains=nome)
                    # Ordenação com base na opção selecionada
            if sort == "az":
                campos = campos.order_by("nome")  # A-Z
            elif sort == "za":
                campos = campos.order_by("-nome")  # Z-A
            elif sort == "recent":
                campos = campos.order_by("-created_at")  # Mais recente
            if campos.exists():
                html = render(request, "components/lista_campos.html", {"campos": campos}).content.decode("utf-8")
            else:
                html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'
            return JsonResponse({"html": html})
        else:
            return JsonResponse({"error": "Invalid request"}, status=400)

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
        current_date = date.today()
        atividades_hoje = self.get_atividades_por_data(request.user, current_date)
        
        context = {
            'atividades_hoje': atividades_hoje,
            'current_date': current_date.strftime('%Y-%m-%d'),  # Formatar a data corretamente
            'current_page': 'home',
        }
        return render(request, 'home.html', context)
    
    def get_atividades_por_data(self, user, data):
        return Evento.objects.filter(data_inicio__lte=data, data_fim__gte=data, campos__agricultor=user)

def atividades_por_data(request, data):
    data = datetime.strptime(data, '%Y-%m-%d').date()
    atividades = HomeView().get_atividades_por_data(request.user, data)
    html = render_to_string('components/atividades_lista.html', {'atividades_hoje': atividades})
    return JsonResponse({'html': html})

""" Calendário """

class CalendarioView(View):
    def get(self, request):
        terrenos = list(request.user.campos.all())
        terreno_id = request.GET.get('terreno_id')

        if terrenos:
            if (terreno_id):
                terreno_atual = get_object_or_404(Campo, id=terreno_id, agricultor=request.user)
            else:
                terreno_atual = terrenos[0]
            
            terreno_index = terrenos.index(terreno_atual) if terreno_atual in terrenos else 0
            terreno_anterior = terrenos[terreno_index - 1] if terreno_index > 0 else terrenos[-1]
            terreno_proximo = terrenos[terreno_index + 1] if terreno_index < len(terrenos) - 1 else terrenos[0]
            
            eventos = list(terreno_atual.eventos.values())
            for evento in eventos:
                evento['data_inicio'] = evento['data_inicio'].strftime('%Y-%m-%d')
                if evento['data_fim']:
                    evento['data_fim'] = evento['data_fim'].strftime('%Y-%m-%d')
        else:
            terreno_atual = "Nenhum campo foi registrado ainda"
            terreno_anterior = None
            terreno_proximo = None
            eventos = []

        context = {
            "eventos": json.dumps(eventos),
            "terreno_atual": terreno_atual,
            "terreno_anterior": terreno_anterior,
            "terreno_proximo": terreno_proximo,
            "terrenos": terrenos,
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
            campo_ids = data.get('campos', [])
            cor = data.get('cor', '#FF5733')

            evento = Evento.objects.create(
                descricao=descricao,
                data_inicio=data_inicio,
                data_fim=data_fim,
                cor=cor
            )

            campos = Campo.objects.filter(id__in=campo_ids)
            evento.campos.set(campos)
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
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                
                if evento.data_inicio == evento.data_fim:
                    evento.delete()
                elif evento.data_inicio == date_obj:
                    evento.data_inicio = date_obj + timedelta(days=1)
                    evento.save()
                elif evento.data_fim == date_obj:
                    evento.data_fim = date_obj - timedelta(days=1)
                    evento.save()
                else:
                    # Criar um novo evento para os dias após o dia excluído
                    novo_evento_apos = Evento.objects.create(
                        descricao=evento.descricao,
                        data_inicio=date_obj + timedelta(days=1),
                        data_fim=evento.data_fim,
                        cor=evento.cor
                    )
                    novo_evento_apos.campos.set(evento.campos.all())
                    
                    # Criar um novo evento para os dias antes do dia excluído
                    novo_evento_antes = Evento.objects.create(
                        descricao=evento.descricao,
                        data_inicio=evento.data_inicio,
                        data_fim=date_obj - timedelta(days=1),
                        cor=evento.cor
                    )
                    novo_evento_antes.campos.set(evento.campos.all())
                    
                    # Excluir o evento original
                    evento.delete()
            else:
                evento.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        user = request.user
        form = ProfileForm(instance=user)
        context = {
            'form': form,
            'nome': user.username,
            'email': user.email,
            'quantidade_campos': user.campos.count(),
        }
        return render(request, 'perfil.html', context)
    def post(self, request):
        user = request.user
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
        context = {
            'form': form,
            'nome': user.username,
            'email': user.email,
            'quantidade_campos': user.campos.count(),
        }
        return render(request, 'perfil.html', context)
    

class CamposView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):

        campos = []  
        context = {
            'campos': campos,
        }
        return render(request, 'campos.html', context)
    
def Filtrar_campos(request):
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        nome = request.GET.get("nome", "")
        tipo = request.GET.get("tipo", "")
        sort = request.GET.get("sort", "az") 
        
        campos = Campo.objects.all()

        if nome:
            campos = campos.filter(nome__icontains=nome)
        
        if sort == "az":
            campos = campos.order_by("nome") 
        elif sort == "za":
            campos = campos.order_by("-nome") 
        elif sort == "recent":
            campos = campos.order_by("-created_at")  

        if campos.exists():
            html = render_to_string("components/lista_campos.html", {"campos": campos}, request=request)
        else:
            html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'

        return JsonResponse({"html": html})
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)